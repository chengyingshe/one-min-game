"""WebSocket endpoint for interactive game streaming."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.database import SessionLocal
from app.services import game_service

router = APIRouter(tags=["ws"])

# Resolve python interpreter
_PYTHON = sys.executable or "python3"

# Stream runner script path
_STREAM_RUNNER = str(Path(__file__).resolve().parent.parent / "game_stream_runner.py")


def _game_dir(name: str) -> Path:
    return Path(settings.GAMES_DIR) / name


@router.websocket("/ws/play/{game_name}")
async def ws_play(websocket: WebSocket, game_name: str):
    """Stream an interactive game session to the browser."""
    # Validate game exists
    db = SessionLocal()
    try:
        game = game_service.get_game(db, game_name)
    finally:
        db.close()

    if not game:
        await websocket.close(code=4040, reason="Game not found")
        return

    game_path = _game_dir(game_name)
    if not game_path.exists():
        await websocket.close(code=4040, reason="Game files not found")
        return

    await websocket.accept()

    # Increment play count
    db2 = SessionLocal()
    try:
        game_service.increment_play_count(db2, game_name)
    finally:
        db2.close()

    # Resolve SDK path so the game can import pygame_sdk
    # Docker: mounted at /sdk; Local: relative from project root
    sdk_candidates = [
        Path("/sdk"),  # Docker mount
        Path(__file__).resolve().parent.parent.parent.parent / "runtime" / "pygame-sdk",  # Local dev
    ]
    sdk_path = ""
    for candidate in sdk_candidates:
        if candidate.exists() and (candidate / "pygame_sdk").is_dir():
            sdk_path = str(candidate)
            break

    # Spawn the game stream runner subprocess
    proc = await asyncio.create_subprocess_exec(
        _PYTHON, _STREAM_RUNNER, str(game_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={
            **__import__("os").environ,
            "SDL_VIDEODRIVER": "dummy",
            "PYTHONPATH": sdk_path + ":" + str(game_path),
        },
    )

    async def read_stdout():
        """Read frames from subprocess stdout and send to WebSocket."""
        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").strip()
                if not text:
                    continue
                # Skip non-JSON lines (e.g. pygame welcome messages on stdout)
                if not text.startswith("{"):
                    continue
                await websocket.send_text(text)
        except Exception:
            pass

    async def read_stderr():
        """Log subprocess stderr for debugging."""
        try:
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                import sys as _sys
                _sys.stderr.write(f"[game] {line.decode('utf-8', errors='replace')}")
        except Exception:
            pass

    async def read_ws():
        """Read keyboard events from WebSocket and write to subprocess stdin."""
        try:
            while True:
                data = await websocket.receive_text()
                if proc.stdin.is_closing():
                    break
                proc.stdin.write((data + "\n").encode("utf-8"))
                await proc.stdin.drain()
        except Exception:
            pass

    try:
        await asyncio.gather(read_stdout(), read_stderr(), read_ws())
    except WebSocketDisconnect:
        pass
    finally:
        # Send error if subprocess exited with failure
        if proc.returncode and proc.returncode != 0:
            try:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Game exited with code {proc.returncode}",
                }))
            except Exception:
                pass
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                proc.kill()
