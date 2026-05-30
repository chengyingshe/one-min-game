"""List available game templates."""

from __future__ import annotations

from pathlib import Path

import yaml

from pygame_studio_mcp.lib.paths import templates_dir
from pygame_studio_mcp.types import PERSPECTIVE_MAP


async def list_templates() -> list[dict]:
    """Scan templates directory and return template metadata."""
    tdir = templates_dir()
    if not tdir.exists():
        return []

    templates: list[dict] = []
    for entry in sorted(tdir.iterdir()):
        if not entry.is_dir():
            continue
        config_path = entry / "config.yaml"
        if not config_path.exists():
            templates.append({
                "name": entry.name,
                "genre": "unknown",
                "perspective": "unknown",
                "description": "",
            })
            continue
        try:
            raw = config_path.read_text(encoding="utf-8")
            config = yaml.safe_load(raw) or {}
            genre = str(config.get("genre", "unknown"))
            templates.append({
                "name": entry.name,
                "genre": genre,
                "perspective": PERSPECTIVE_MAP.get(genre, "unknown"),
                "description": str(
                    config.get("description", "")
                    or (config.get("gameplay") or {}).get("objective", "")
                ),
            })
        except Exception:
            templates.append({
                "name": entry.name,
                "genre": "unknown",
                "perspective": "unknown",
                "description": "",
            })

    return templates
