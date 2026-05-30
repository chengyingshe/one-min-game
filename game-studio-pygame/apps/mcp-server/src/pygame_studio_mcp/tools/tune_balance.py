"""Adjust game difficulty based on feedback."""

from __future__ import annotations

from pygame_studio_mcp.lib.balance_tuner import tune_balance
from pygame_studio_mcp.lib.paths import project_dir


async def tune_balance_tool(project: str, feedback: str) -> dict:
    """Tune config.yaml difficulty parameters based on natural-language feedback."""
    dir_path = project_dir(project)
    config_path = dir_path / "config.yaml"

    if not config_path.exists():
        return {"changes": {}}

    result = tune_balance(config_path, feedback)
    return {"changes": result.changes}
