from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class PlatformerConfig:
    name: str = "pixel-runner"
    screen_width: int = 800
    screen_height: int = 600
    fps: int = 60
    player_color: tuple[int, int, int] = (50, 150, 255)
    player_size: tuple[int, int] = (24, 32)
    enemy_color: tuple[int, int, int] = (200, 50, 50)
    enemy_size: tuple[int, int] = (24, 24)
    platform_color: tuple[int, int, int] = (100, 100, 120)
    ground_color: tuple[int, int, int] = (60, 60, 80)
    bg_color: tuple[int, int, int] = (15, 15, 35)
    coin_color: tuple[int, int, int] = (255, 220, 50)
    coin_size: tuple[int, int] = (12, 12)
    difficulty: dict = None

    def __post_init__(self):
        if self.difficulty is None:
            self.difficulty = {}

    def params(self, tier: str = "normal") -> dict:
        return self.difficulty.get(tier, self.difficulty.get("normal", {}))


def load_config(path: str = "config.yaml") -> PlatformerConfig:
    p = Path(path)
    if not p.exists():
        return default_config()
    with open(p) as f:
        raw = yaml.safe_load(f) or {}

    screen = raw.get("screen", {})
    player = raw.get("player", {})
    pc = player.get("color", [50, 150, 255])
    if isinstance(pc, list):
        pc = tuple(pc[:3])

    return PlatformerConfig(
        name=raw.get("name", "pixel-runner"),
        screen_width=screen.get("width", 800),
        screen_height=screen.get("height", 600),
        fps=screen.get("fps", 60),
        player_color=pc,
        difficulty=raw.get("difficulty", {}),
    )


def default_config() -> PlatformerConfig:
    return PlatformerConfig(
        difficulty={
            "easy": {"gravity": 0.4, "jump_impulse": -12, "player_speed": 4, "enemy_speed": 1.0, "spawn_rate": 150, "grace_period": 120},
            "normal": {"gravity": 0.6, "jump_impulse": -13, "player_speed": 5, "enemy_speed": 2.0, "spawn_rate": 100, "grace_period": 90},
            "hard": {"gravity": 0.9, "jump_impulse": -14, "player_speed": 6, "enemy_speed": 3.5, "spawn_rate": 70, "grace_period": 60},
        }
    )
