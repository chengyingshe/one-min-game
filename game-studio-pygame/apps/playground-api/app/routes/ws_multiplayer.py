"""WebSocket endpoint for multiplayer game streaming.

Architecture: Each player has their own WebSocket handler.
- The host handler spawns the subprocess and reads stdout (broadcasts frames).
- Each player's handler forwards their own keyboard input to subprocess stdin.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.services.room_service import room_service
import logging

log = logging.getLogger("ws_multiplayer")

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
        # Phase 1: Lobby — wait for host to start the game
        while room.status == "waiting":
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "start_game" and player_id == room.host_id:
                log.info("Host %s starting game in room %s", player_id, room_id)
                await _start_game(room)
                # Host falls through to game mode below
                break
            # Non-host messages during lobby are ignored

        # Phase 2: Game — forward this player's input to subprocess
        if room.status in ("running", "starting", "finished"):
            is_host = player_id == room.host_id
            log.info("Player %s entering game loop (host=%s)", player_id, is_host)
            await _player_game_loop(room, websocket, player_id, is_host)
            log.info("Player %s game loop ended", player_id)

    except WebSocketDisconnect:
        log.info("Player %s disconnected from room %s", player_id, room_id)
    except Exception as exc:
        log.exception("Error for player %s in room %s: %s", player_id, room_id, exc)
    finally:
        player_info.websocket = None
        room_service.remove_player(room_id, player_id)


async def _start_game(room) -> None:
    """Spawn the game subprocess (called by host handler only)."""
    room.status = "starting"
    game_path = _game_dir(room.game_name)

    if not game_path.exists():
        await _broadcast(room, json.dumps({"type": "error", "message": "Game files not found"}))
        room.status = "waiting"
        return

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
        limit=2**20,  # 1MB buffer for large base64 JPEG frames
        env={
            **os.environ,
            "SDL_VIDEODRIVER": "dummy",
            "PYTHONPATH": sdk_path + ":" + str(game_path),
        },
    )
    room.process = proc
    room.status = "running"

    # Send start_game to subprocess with player info
    players_data = [
        {"id": pid, "name": p.display_name, "color": list(p.color)}
        for pid, p in room.players.items()
    ]
    start_msg = json.dumps({"type": "start_game", "players": players_data}) + "\n"
    proc.stdin.write(start_msg.encode())
    await proc.stdin.drain()

    # Notify all clients
    await _broadcast(room, json.dumps({"type": "game_start", "players": players_data}))


async def _player_game_loop(room, websocket: WebSocket, player_id: str, is_host: bool):
    """Each player runs this during the game.

    - Host: reads stdout + own input in parallel
    - Non-host: forwards own input to subprocess
    """
    proc = room.process

    if is_host and proc:
        # Host manages subprocess stdout and their own input
        await asyncio.gather(
            _read_stdout(room, proc),
            _read_stderr(proc),
            _forward_input(player_id, websocket, proc),
        )
        # Cleanup subprocess when host exits
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                proc.kill()
        room.status = "finished"
    else:
        # Non-host: just forward input until game ends or disconnect
        await _forward_input(player_id, websocket, proc)


async def _read_stdout(room, proc):
    """Read frames from subprocess stdout and broadcast to all players."""
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").strip()
            if not text or not text.startswith("{"):
                continue
            await _broadcast(room, text)
            try:
                msg = json.loads(text)
                if msg.get("type") == "gameover":
                    room.status = "finished"
            except Exception:
                pass
    except Exception as e:
        log.error("stdout read error: %s", e)


async def _read_stderr(proc):
    """Drain stderr to prevent pipe blocking."""
    try:
        while True:
            line = await proc.stderr.readline()
            if not line:
                break
            log.warning("[game stderr] %s", line.decode("utf-8", errors="replace").rstrip())
    except Exception:
        pass


async def _forward_input(player_id: str, websocket: WebSocket, proc):
    """Read from one player's WebSocket and forward tagged input to subprocess."""
    try:
        while True:
            data = await websocket.receive_text()
            if proc is None or proc.stdin.is_closing():
                break
            try:
                msg = json.loads(data)
                msg["player"] = player_id
                proc.stdin.write((json.dumps(msg) + "\n").encode())
                await proc.stdin.drain()
            except Exception:
                pass
    except Exception:
        # Player disconnected
        if proc and not proc.stdin.is_closing():
            try:
                proc.stdin.write(
                    (json.dumps({"type": "player_left", "player_id": player_id}) + "\n").encode()
                )
                await proc.stdin.drain()
            except Exception:
                pass
