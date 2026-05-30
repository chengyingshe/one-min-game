"""Validate a game runs without crashing."""

from __future__ import annotations

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.paths import project_dir


async def validate_gameplay(project: str) -> dict:
    """Run the game briefly to check for crashes."""
    dir_path = project_dir(project)
    main_py = dir_path / "main.py"

    if not main_py.exists():
        return {"valid": False, "issues": ["main.py not found. Run build_game first."]}

    # Run for 3 seconds in headless mode
    result = run(
        ["python3", "main.py"],
        cwd=str(dir_path),
        timeout=3,
        env={"SDL_VIDEODRIVER": "dummy"},
    )

    issues: list[str] = []

    if result.timed_out:
        # Timeout is expected for an interactive game - means it didn't crash
        return {"valid": True, "issues": []}

    if result.returncode != 0:
        issues.append(
            f"Game exited with code {result.returncode}: {result.stderr[:500]}"
        )

    return {"valid": len(issues) == 0, "issues": issues}
