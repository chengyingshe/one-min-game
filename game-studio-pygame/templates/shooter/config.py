from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ShooterConfig:
    name: str = "space-blaster"
    screen_width: int = 800
    screen_height: int = 600
    fps: int = 60
    player_color: tuple[int, int, int] = (0, 200, 100)
    player_size: tuple[int, int] = (24, 24)
    enemy_color: tuple[int, int, int] = (200, 50, 50)
    enemy_size: tuple[int, int] = (20, 20)
    bullet_color: tuple[int, int, int] = (255, 255, 100)
    bullet_size: tuple[int, int] = (4, 12)
    bg_color: tuple[int, int, int] = (10, 10, 30)
    difficulty: dict = None

    def __post_init__(self):
        if self.difficulty is None:
            self.difficulty = {}

    def params(self, tier: str = "normal") -> dict:
        return self.difficulty.get(tier, self.difficulty.get("normal", {}))


def load_config(path: str = "config.yaml") -> ShooterConfig:
    p = Path(path)
    if not p.exists():
        return default_config()
    with open(p) as f:
        raw = yaml.safe_load(f) or {}

    screen = raw.get("screen", {})
    player = raw.get("player", {})
    pc = player.get("color", [0, 200, 100])
    if isinstance(pc, list):
        pc = tuple(pc[:3])

    return ShooterConfig(
        name=raw.get("name", "space-blaster"),
        screen_width=screen.get("width", 800),
        screen_height=screen.get("height", 600),
        fps=screen.get("fps", 60),
        player_color=pc,
        difficulty=raw.get("difficulty", {}),
    )


def default_config() -> ShooterConfig:
    return ShooterConfig(
        difficulty={
            "easy": {"enemy_speed": 1.5, "spawn_rate": 100, "player_hp": 6, "bullet_speed": 6, "grace_period": 120},
            "normal": {"enemy_speed": 3.0, "spawn_rate": 65, "player_hp": 4, "bullet_speed": 5, "grace_period": 90},
            "hard": {"enemy_speed": 4.5, "spawn_rate": 40, "player_hp": 2, "bullet_speed": 4, "grace_period": 60},
        }
    )
