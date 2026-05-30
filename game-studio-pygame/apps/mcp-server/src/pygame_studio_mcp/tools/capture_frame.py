"""Capture a frame of game output (stdout from short run)."""

from __future__ import annotations

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.paths import project_dir


async def capture_frame(project: str) -> dict:
    """Run the game briefly and capture stdout output."""
    dir_path = project_dir(project)
    main_py = dir_path / "main.py"

    if not main_py.exists():
        return {"frame": "(main.py not found)"}

    result = run(
        ["python3", "main.py"],
        cwd=str(dir_path),
        timeout=1,
        env={"SDL_VIDEODRIVER": "dummy"},
    )

    output = result.stdout or result.stderr or "(no output captured)"
    if len(output) > 4000:
        output = output[:4000] + "\n...(truncated)"

    return {"frame": output}
