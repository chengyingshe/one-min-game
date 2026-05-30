"""Create a new game project directory."""

from __future__ import annotations

from pygame_studio_mcp.lib.paths import generated_games_dir, project_dir


async def create_project(name: str) -> dict:
    """Create a project directory under generated-games/."""
    base_dir = generated_games_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    dir_path = project_dir(name)
    if dir_path.exists():
        return {"path": str(dir_path), "status": "already_exists"}

    dir_path.mkdir(parents=True, exist_ok=True)
    return {"path": str(dir_path), "status": "created"}
