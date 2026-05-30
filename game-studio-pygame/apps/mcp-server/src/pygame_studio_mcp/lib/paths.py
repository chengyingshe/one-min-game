"""Path resolution for the PyGame Studio project layout."""

from __future__ import annotations

import os
from pathlib import Path


def get_studio_root() -> Path:
    """Return the project root, checking GAME_STUDIO_ROOT env var first."""
    env_root = os.environ.get("GAME_STUDIO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # Default: assume this file is at apps/mcp-server/src/pygame_studio_mcp/lib/paths.py
    return Path(__file__).resolve().parents[6]


def templates_dir() -> Path:
    return get_studio_root() / "templates"


def generated_games_dir() -> Path:
    return get_studio_root() / "generated-games"


def runtime_dir() -> Path:
    return get_studio_root() / "runtime"


def project_dir(name: str) -> Path:
    return generated_games_dir() / name


def sdk_dir() -> Path:
    return runtime_dir() / "pygame-sdk"


def sdk_api_file() -> Path:
    return sdk_dir() / "pygame_sdk" / "__init__.py"
