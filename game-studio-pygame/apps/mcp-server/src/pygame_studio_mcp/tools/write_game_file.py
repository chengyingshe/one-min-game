"""Write or overwrite a file in a game project."""

from __future__ import annotations

import re
from pathlib import Path

from pygame_studio_mcp.lib.paths import project_dir

_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+\.(py|yaml|txt|md|toml|cfg|json)$")
_PROJECT_RE = re.compile(r"^[a-zA-Z0-9\-]+$")


async def write_game_file(project: str, filename: str, content: str) -> dict:
    """Write a file to a project directory."""
    if not _PROJECT_RE.match(project):
        return {"success": False, "path": "", "bytes_written": 0}
    if not _FILENAME_RE.match(filename):
        return {"success": False, "path": "", "bytes_written": 0}

    dir_path = project_dir(project)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / filename
    file_path.write_text(content, encoding="utf-8")

    return {
        "success": True,
        "path": str(file_path),
        "bytes_written": len(content.encode("utf-8")),
    }
