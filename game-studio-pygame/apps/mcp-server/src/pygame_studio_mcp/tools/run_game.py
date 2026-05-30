"""Run a Python game project."""

from __future__ import annotations

import os

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.paths import project_dir


async def run_game(project: str, duration: float | None = None) -> dict:
    """Run a game with SDL_VIDEODRIVER=dummy for headless execution."""
    dir_path = project_dir(project)
    main_py = dir_path / "main.py"

    if not main_py.exists():
        return {"pid": None, "status": "error: main.py not found"}

    timeout = (duration or 60)
    env = {"SDL_VIDEODRIVER": "dummy"}
    result = run(
        ["python3", "main.py"],
        cwd=str(dir_path),
        timeout=timeout,
        env=env,
    )

    if result.timed_out:
        return {"pid": None, "status": "timeout"}
    if result.returncode == 0:
        return {"pid": None, "status": "exited_cleanly", "output": result.stdout}
    return {
        "pid": None,
        "status": f"exited_with_code_{result.returncode}",
        "stderr": result.stderr[:500],
    }
