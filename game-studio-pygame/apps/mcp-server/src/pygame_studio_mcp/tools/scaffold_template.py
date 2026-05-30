"""Copy template files into a project directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from pygame_studio_mcp.lib.paths import project_dir, templates_dir


async def scaffold_template(template: str, project: str) -> dict:
    """Copy template files into a generated-games project directory."""
    src = templates_dir() / template
    dest = project_dir(project)

    if not src.exists():
        return {"success": False, "path": str(dest), "error": f"Template '{template}' not found"}

    try:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        return {"success": True, "path": str(dest)}
    except Exception as exc:
        return {"success": False, "path": str(dest), "error": str(exc)}
