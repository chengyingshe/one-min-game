"""Game configuration loading from YAML with pixel-based dimensions."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .difficulty import DifficultyParams
from .vector import Vector2D


@dataclass
class ScreenConfig:
    width: int = 800
    height: int = 600
    fps: int = 60


@dataclass
class PlayerConfig:
    symbol: str = "@"
    hp: int = 1
    speed: float = 200.0
    attack: int = 1
    color: tuple[int, int, int] = (255, 255, 0)
    position: Vector2D = field(default_factory=Vector2D)


@dataclass
class ControlsConfig:
    move: str = "arrows"
    attack: str = "space"


@dataclass
class GameplayConfig:
    objective: str = "score"
    duration: int = 0


@dataclass
class MultiplayerConfig:
    enabled: bool = False
    max_players: int = 4
    min_players: int = 2
    shared_viewport: bool = True
    player_colors: list[tuple[int, int, int]] = field(default_factory=lambda: [
        (255, 220, 50),
        (80, 160, 255),
        (80, 220, 80),
        (220, 80, 80),
    ])


@dataclass
class GameConfig:
    """Top-level game configuration loaded from config.yaml."""

    name: str = "untitled"
    genre: str = "arcade"
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    player: PlayerConfig = field(default_factory=PlayerConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
    gameplay: GameplayConfig = field(default_factory=GameplayConfig)
    difficulty: dict[str, DifficultyParams] = field(default_factory=dict)
    multiplayer: MultiplayerConfig = field(default_factory=MultiplayerConfig)


def default_game_config() -> GameConfig:
    """Return a sensible default configuration."""
    return GameConfig(
        screen=ScreenConfig(width=800, height=600, fps=60),
        player=PlayerConfig(symbol="@", hp=1, speed=200.0),
        controls=ControlsConfig(move="arrows", attack="space"),
        gameplay=GameplayConfig(objective="score", duration=0),
        difficulty={
            "easy": DifficultyParams(
                tier="easy", gravity=300.0, speed=1.0, spawn_rate=90, grace_period=35
            ),
            "normal": DifficultyParams(
                tier="normal", gravity=500.0, speed=1.0, spawn_rate=60, grace_period=25
            ),
            "hard": DifficultyParams(
                tier="hard", gravity=700.0, speed=2.0, spawn_rate=40, grace_period=15
            ),
        },
    )


def load_config(path: str | Path) -> GameConfig:
    """Load a GameConfig from a YAML file.

    Missing fields fall back to defaults.
    """
    path = Path(path)
    if not path.exists():
        return default_game_config()

    with open(path) as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    return _parse_config(raw)


def load_config_from_string(yaml_str: str) -> GameConfig:
    """Load a GameConfig from a YAML string."""
    raw: dict[str, Any] = yaml.safe_load(yaml_str) or {}
    return _parse_config(raw)


def _parse_config(raw: dict[str, Any]) -> GameConfig:
    """Parse a raw dict into a GameConfig."""
    defaults = default_game_config()

    screen_raw = raw.get("screen", {})
    screen = ScreenConfig(
        width=screen_raw.get("width", defaults.screen.width),
        height=screen_raw.get("height", defaults.screen.height),
        fps=screen_raw.get("fps", defaults.screen.fps),
    )

    player_raw = raw.get("player", {})
    player_color = player_raw.get("color", list(defaults.player.color))
    if isinstance(player_color, list):
        player_color = tuple(player_color[:3])  # type: ignore[assignment]
    pos_raw = player_raw.get("position", {})
    player_pos = Vector2D(pos_raw.get("x", 0), pos_raw.get("y", 0)) if isinstance(pos_raw, dict) else defaults.player.position
    player = PlayerConfig(
        symbol=player_raw.get("symbol", defaults.player.symbol),
        hp=player_raw.get("hp", defaults.player.hp),
        speed=float(player_raw.get("speed", defaults.player.speed)),
        attack=player_raw.get("attack", defaults.player.attack),
        color=player_color,  # type: ignore[arg-type]
        position=player_pos,
    )

    controls_raw = raw.get("controls", {})
    controls = ControlsConfig(
        move=controls_raw.get("move", defaults.controls.move),
        attack=controls_raw.get("attack", defaults.controls.attack),
    )

    gameplay_raw = raw.get("gameplay", {})
    gameplay = GameplayConfig(
        objective=gameplay_raw.get("objective", defaults.gameplay.objective),
        duration=gameplay_raw.get("duration", defaults.gameplay.duration),
    )

    difficulty: dict[str, DifficultyParams] = {}
    diff_raw = raw.get("difficulty", {})
    if isinstance(diff_raw, dict):
        for tier_name, params in diff_raw.items():
            if isinstance(params, dict):
                difficulty[tier_name] = DifficultyParams(
                    tier=tier_name,
                    gravity=float(params.get("gravity", 0)),
                    speed=float(params.get("speed", 1.0)),
                    spawn_rate=int(params.get("spawn_rate", 60)),
                    grace_period=int(params.get("grace_period", 25)),
                    hp_bonus=int(params.get("hp_bonus", 0)),
                    gap_size=int(params.get("gap_size", 0)),
                    flap_impulse=float(params.get("flap_impulse", 0)),
                )

    if not difficulty:
        difficulty = defaults.difficulty

    mp_raw = raw.get("multiplayer", {})
    if isinstance(mp_raw, dict) and mp_raw:
        colors_raw = mp_raw.get("player_colors", [])
        player_colors = []
        for c in colors_raw:
            if isinstance(c, (list, tuple)) and len(c) >= 3:
                player_colors.append(tuple(c[:3]))
        if not player_colors:
            player_colors = defaults.multiplayer.player_colors
        multiplayer = MultiplayerConfig(
            enabled=mp_raw.get("enabled", False),
            max_players=int(mp_raw.get("max_players", 4)),
            min_players=int(mp_raw.get("min_players", 2)),
            shared_viewport=mp_raw.get("shared_viewport", True),
            player_colors=player_colors,
        )
    else:
        multiplayer = defaults.multiplayer

    return GameConfig(
        name=raw.get("name", defaults.name),
        genre=raw.get("genre", defaults.genre),
        screen=screen,
        player=player,
        controls=controls,
        gameplay=gameplay,
        difficulty=difficulty,
        multiplayer=multiplayer,
    )
