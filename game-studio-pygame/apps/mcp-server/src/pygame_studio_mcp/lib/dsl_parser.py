"""GameSpec validation and YAML serialization."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import yaml

from pygame_studio_mcp.types import (
    VALID_GENRES,
    BulletSpec,
    ControlsSpec,
    GameplaySpec,
    GameSpec,
    PlayerSpec,
    ScreenSpec,
    EnemySpec,
)


def _validate_str(data: Any, field_name: str) -> str:
    if not isinstance(data, str):
        raise ValueError(f"{field_name} must be a string")
    return data


def _validate_genre(data: Any) -> str:
    if not isinstance(data, str) or data not in VALID_GENRES:
        raise ValueError(f"genre must be one of {VALID_GENRES}")
    return data


def _validate_int_or_none(data: Any) -> int | None:
    if data is None:
        return None
    if not isinstance(data, int):
        raise ValueError("expected int")
    return data


def _validate_float_or_none(data: Any) -> float | None:
    if data is None:
        return None
    if isinstance(data, (int, float)):
        return float(data)
    raise ValueError("expected number")
    return None  # unreachable, but satisfies type checker


def _parse_screen(data: Any) -> ScreenSpec:
    if not isinstance(data, dict):
        raise ValueError("screen must be an object")
    return ScreenSpec(
        width=int(data.get("width", 800)),
        height=int(data.get("height", 600)),
        fps=int(data.get("fps", 60)),
    )


def _parse_player(data: Any) -> PlayerSpec:
    if not isinstance(data, dict):
        raise ValueError("player must be an object")
    return PlayerSpec(
        symbol=_validate_str(data.get("symbol", "@"), "player.symbol"),
        hp=_validate_int_or_none(data.get("hp")),
        speed=_validate_float_or_none(data.get("speed")),
        attack=_validate_float_or_none(data.get("attack")),
        color=data.get("color"),
    )


def _parse_enemy(data: Any) -> EnemySpec:
    if not isinstance(data, dict):
        raise ValueError("enemy must be an object")
    return EnemySpec(
        symbol=_validate_str(data.get("symbol", "E"), "enemy.symbol"),
        speed=_validate_float_or_none(data.get("speed")),
        spawn_rate=_validate_float_or_none(data.get("spawn_rate")),
        hp=_validate_int_or_none(data.get("hp")),
        count=_validate_int_or_none(data.get("count")),
    )


def _parse_bullet(data: Any) -> BulletSpec:
    if not isinstance(data, dict):
        raise ValueError("bullet must be an object")
    return BulletSpec(
        symbol=_validate_str(data.get("symbol", "*"), "bullet.symbol"),
        speed=float(data.get("speed", 10.0)),
    )


def _parse_controls(data: Any) -> ControlsSpec:
    if not isinstance(data, dict):
        raise ValueError("controls must be an object")
    return ControlsSpec(
        move=_validate_str(data.get("move", "arrows"), "controls.move"),
        attack=_validate_str(data.get("attack", "space"), "controls.attack"),
    )


def _parse_gameplay(data: Any) -> GameplaySpec:
    if not isinstance(data, dict):
        raise ValueError("gameplay must be an object")
    return GameplaySpec(
        objective=_validate_str(data.get("objective", ""), "gameplay.objective"),
        duration=int(data.get("duration", 0)),
    )


def _parse_difficulty(data: Any) -> dict[str, dict[str, float]]:
    if not isinstance(data, dict):
        raise ValueError("difficulty must be an object")
    result: dict[str, dict[str, float]] = {}
    for tier, params in data.items():
        if not isinstance(params, dict):
            raise ValueError(f"difficulty.{tier} must be an object")
        result[str(tier)] = {}
        for k, v in params.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"difficulty.{tier}.{k} must be a number")
            result[str(tier)][str(k)] = float(v)
    return result


class ParseResult:
    def __init__(
        self, success: bool, spec: GameSpec | None = None, error: str | None = None
    ):
        self.success = success
        self.spec = spec
        self.error = error


def parse_game_spec(yaml_string: str) -> ParseResult:
    """Parse and validate a YAML game spec string."""
    try:
        raw = yaml.safe_load(yaml_string)
        if not isinstance(raw, dict):
            return ParseResult(success=False, error="Spec must be a YAML mapping")

        spec = GameSpec(
            name=_validate_str(raw.get("name", ""), "name"),
            genre=_validate_genre(raw.get("genre", "shooter")),
        )

        if "perspective" in raw:
            spec.perspective = _validate_str(raw["perspective"], "perspective")
        if "screen" in raw:
            spec.screen = _parse_screen(raw["screen"])
        if "player" in raw:
            spec.player = _parse_player(raw["player"])
        if "enemy" in raw:
            spec.enemy = _parse_enemy(raw["enemy"])
        if "bullet" in raw:
            spec.bullet = _parse_bullet(raw["bullet"])
        if "controls" in raw:
            spec.controls = _parse_controls(raw["controls"])
        if "gameplay" in raw:
            spec.gameplay = _parse_gameplay(raw["gameplay"])
        if "difficulty" in raw:
            spec.difficulty = _parse_difficulty(raw["difficulty"])

        return ParseResult(success=True, spec=spec)
    except Exception as exc:
        return ParseResult(success=False, error=str(exc))


def spec_to_yaml(spec: GameSpec) -> str:
    """Serialize a GameSpec to YAML string."""
    return yaml.safe_dump(asdict(spec), default_flow_style=False, allow_unicode=True)
