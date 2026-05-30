"""Difficulty parameter tuning based on natural-language feedback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TuneResult:
    def __init__(self, changes: dict[str, dict[str, float]] | None = None):
        self.changes: dict[str, dict[str, float]] = changes or {}


# Mapping of feedback keywords to parameter adjustments
TUNING_RULES: list[dict[str, Any]] = [
    {
        "keywords": ["too hard", "too difficult", "impossible"],
        "adjustments": {"gravity": -0.02, "speed": -0.1, "spawn_rate": 5},
    },
    {
        "keywords": ["too easy", "boring", "too slow"],
        "adjustments": {"gravity": 0.02, "speed": 0.1, "spawn_rate": -5},
    },
    {
        "keywords": ["too fast", "overwhelming"],
        "adjustments": {"spawn_rate": 5, "speed": -0.2},
    },
]


def _apply_adjustment(
    obj: dict[str, Any],
    key: str,
    delta: float,
    changes: dict[str, dict[str, float]],
) -> None:
    """Recursively search for *key* in *obj* and apply *delta*."""
    for k, v in list(obj.items()):
        if k == key and isinstance(v, (int, float)):
            old_val = float(v)
            new_val = old_val + delta
            obj[k] = new_val
            changes[key] = {"before": old_val, "after": new_val}
        elif isinstance(v, dict):
            _apply_adjustment(v, key, delta, changes)


def tune_balance(config_path: Path, feedback: str) -> TuneResult:
    """Read config, apply tuning rules, write back, return changes."""
    content = config_path.read_text(encoding="utf-8")
    config = yaml.safe_load(content) or {}
    if not isinstance(config, dict):
        return TuneResult()

    changes: dict[str, dict[str, float]] = {}
    lower_feedback = feedback.lower()

    for rule in TUNING_RULES:
        if not any(kw in lower_feedback for kw in rule["keywords"]):
            continue
        for key, delta in rule["adjustments"].items():
            _apply_adjustment(config, key, float(delta), changes)

    updated = yaml.safe_dump(config, default_flow_style=False, allow_unicode=True)
    config_path.write_text(updated, encoding="utf-8")

    return TuneResult(changes=changes)
