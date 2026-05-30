"""Configuration loader."""

from typing import Any

import yaml


def load_config(path: str) -> dict[str, Any] | None:
    """Load config from YAML file. Returns None on failure."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except (FileNotFoundError, yaml.YAMLError):
        return None


def default_config() -> dict[str, Any]:
    """Return sensible defaults."""
    return {
        "name": "dark-room-chronicles",
        "screen": {"width": 800, "height": 600, "fps": 60},
    }
