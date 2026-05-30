"""Read a file from a game project."""

from __future__ import annotations

import re
from pathlib import Path

from pygame_studio_mcp.lib.paths import project_dir

_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+\.(py|yaml|txt|md|toml|cfg|json)$")
_PROJECT_RE = re.compile(r"^[a-zA-Z0-9\-]+$")


async def read_game_file(project: str, filename: str) -> dict:
    """Read a file from a project directory."""
    if not _PROJECT_RE.match(project):
        return {"success": False, "content": "", "error": "Invalid project name"}
    if not _FILENAME_RE.match(filename):
        return {"success": False, "content": "", "error": "Invalid filename"}

    file_path = project_dir(project) / filename
    try:
        content = file_path.read_text(encoding="utf-8")
        return {"success": True, "content": content}
    except FileNotFoundError:
        return {"success": False, "content": "", "error": f"File not found: {filename}"}
    except Exception as exc:
        return {"success": False, "content": "", "error": str(exc)}
