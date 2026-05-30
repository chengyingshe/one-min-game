"""WebSocket endpoint for multiplayer game streaming."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.services.room_service import room_service

router = APIRouter(tags=["ws-multiplayer"])

_PYTHON = sys.executable or "python3"
_STREAM_RUNNER = str(Path(__file__).resolve().parent.parent / "game_stream_runner.py")


def _game_dir(name: str) -> Path:
    return Path(settings.GAMES_DIR) / name


async def _broadcast(room, message: str, exclude: str | None = None):
    for pid, p in room.players.items():
        if pid == exclude or p.websocket is None:
            continue
        try:
            await p.websocket.send_text(message)
        except Exception:
            pass


@router.websocket("/ws/multiplayer/{room_id}")
async def ws_multiplayer(websocket: WebSocket, room_id: str):
    room = room_service.get_room(room_id)
    if not room:
        await websocket.close(code=4040, reason="Room not found")
        return

    await websocket.accept()

    # First message must be join
    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        if msg.get("type") != "join":
            await websocket.close(code=4000, reason="Must join first")
            return
    except Exception:
        await websocket.close(code=4000, reason="Invalid join")
        return

    player_name = msg.get("name", "Player")

    # First player to join becomes the host
    is_first = len(room.players) == 0
    player_info = room_service.add_player(room_id, player_name)
    if not player_info:
        await websocket.close(code=4003, reason="Room full or not joinable")
        return

    if is_first:
        room.host_id = player_info.player_id

    player_info.websocket = websocket
    player_id = player_info.player_id

    # Broadcast lobby update
    lobby_msg = json.dumps({
        "type": "lobby",
        "room_code": room_id,
        "host": room.host_id,
        "players": [
            {"id": pid, "name": p.display_name, "color": list(p.color)}
            for pid, p in room.players.items()
        ],
    })
    await _broadcast(room, lobby_msg)

    # Send player their identity
    await websocket.send_text(json.dumps({
        "type": "joined",
        "player_id": player_id,
        "color": list(player_info.color),
    }))

    try:
        while room.status == "waiting":
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "start_game" and player_id == room.host_id:
                # Start the game
                room.status = "starting"
                game_path = _game_dir(room.game_name)
                if not game_path.exists():
                    await _broadcast(room, json.dumps({"type": "error", "message": "Game files not found"}))
                    room.status = "waiting"
                    continue

                # Resolve SDK path
                sdk_candidates = [
                    Path("/sdk"),
                    Path(__file__).resolve().parent.parent.parent.parent / "runtime" / "pygame-sdk",
                ]
                sdk_path = ""
                for c in sdk_candidates:
                    if c.exists() and (c / "pygame_sdk").is_dir():
                        sdk_path = str(c)
                        break

                proc = await asyncio.create_subprocess_exec(
                    _PYTHON, _STREAM_RUNNER, str(game_path),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env={
                        **os.environ,
                        "SDL_VIDEODRIVER": "dummy",
                        "PYTHONPATH": sdk_path + ":" + str(game_path),
                    },
                )
                room.process = proc
                room.status = "running"

                # Send start_game to subprocess
                players_data = [
                    {"id": pid, "name": p.display_name, "color": list(p.color)}
                    for pid, p in room.players.items()
                ]
                start_msg = json.dumps({"type": "start_game", "players": players_data}) + "\n"
                proc.stdin.write(start_msg.encode())
                await proc.stdin.drain()

                # Notify all clients
                await _broadcast(room, json.dumps({"type": "game_start", "players": players_data}))

                # Run the game streaming
                await _run_game(room, proc)
                return

    except WebSocketDisconnect:
        pass
    finally:
        player_info.websocket = None
        room_service.remove_player(room_id, player_id)


async def _run_game(room, proc):
    """Run the game subprocess and coordinate all players."""

    async def read_stdout():
        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").strip()
                if not text or not text.startswith("{"):
                    continue
                await _broadcast(room, text)
                # Check for gameover
                try:
                    msg = json.loads(text)
                    if msg.get("type") == "gameover":
                        room.status = "finished"
                except Exception:
                    pass
        except Exception:
            pass

    async def read_stderr():
        try:
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
        except Exception:
            pass

    async def read_all_players():
        """Read from all player websockets and forward tagged input to subprocess."""
        tasks = {}
        for pid, p in list(room.players.items()):
            if p.websocket:
                tasks[pid] = asyncio.create_task(_read_player_ws(pid, p.websocket, proc))

        if not tasks:
            return

        done, pending = await asyncio.wait(
            tasks.values(), return_when=asyncio.ALL_COMPLETED
        )
        for t in pending:
            t.cancel()

    async def _read_player_ws(pid, ws, proc):
        try:
            while True:
                data = await ws.receive_text()
                if proc.stdin.is_closing():
                    break
                # Tag the message with player id
                try:
                    msg = json.loads(data)
                    msg["player"] = pid
                    proc.stdin.write((json.dumps(msg) + "\n").encode())
                    await proc.stdin.drain()
                except Exception:
                    pass
        except Exception:
            # Player disconnected
            try:
                if not proc.stdin.is_closing():
                    proc.stdin.write(
                        (json.dumps({"type": "player_left", "player_id": pid}) + "\n").encode()
                    )
                    await proc.stdin.drain()
            except Exception:
                pass
            room_service.remove_player(room.room_id, pid)

    try:
        await asyncio.gather(read_stdout(), read_stderr(), read_all_players())
    except Exception:
        pass
    finally:
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                proc.kill()
        room.status = "finished"
