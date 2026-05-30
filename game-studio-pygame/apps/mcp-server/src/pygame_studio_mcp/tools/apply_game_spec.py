"""Merge a game spec into a project's config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pygame_studio_mcp.lib.paths import project_dir
from pygame_studio_mcp.lib.dsl_parser import parse_game_spec, spec_to_yaml
from pygame_studio_mcp.types import GameSpec


def _deep_merge(
    base: dict[str, Any], override: dict[str, Any]
) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        elif value is not None:
            result[key] = value
    return result


async def apply_game_spec(project: str, spec: dict) -> dict:
    """Validate spec, merge with existing config, write config.yaml."""
    dir_path = project_dir(project)
    config_path = dir_path / "config.yaml"

    # Validate via YAML round-trip
    yaml_str = yaml.safe_dump(spec, default_flow_style=False, allow_unicode=True)
    result = parse_game_spec(yaml_str)
    if not result.success:
        return {"success": False, "error": result.error}

    new_spec = result.spec
    if new_spec is None:
        return {"success": False, "error": "Failed to parse spec"}

    # Convert spec to plain dict for merging
    from dataclasses import asdict
    new_dict = asdict(new_spec)

    # Merge with existing config if present
    if config_path.exists():
        try:
            existing = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            if isinstance(existing, dict):
                merged = _deep_merge(existing, new_dict)
            else:
                merged = new_dict
        except Exception:
            merged = new_dict
    else:
        merged = new_dict

    dir_path.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.safe_dump(merged, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return {"success": True}
