from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class FlappyConfig:
    name: str = "flappy"
    screen_width: int = 800
    screen_height: int = 600
    fps: int = 60
    player_color: tuple[int, int, int] = (255, 255, 0)
    pipe_color: tuple[int, int, int] = (0, 180, 0)
    bg_color: tuple[int, int, int] = (20, 20, 40)
    ground_color: tuple[int, int, int] = (80, 60, 40)
    player_size: tuple[int, int] = (30, 24)
    pipe_width: int = 60
    ground_height: int = 40
    difficulty: dict = None

    def __post_init__(self):
        if self.difficulty is None:
            self.difficulty = {}

    def params(self, tier: str = "normal") -> dict:
        return self.difficulty.get(tier, self.difficulty.get("normal", {}))


def load_config(path: str = "config.yaml") -> FlappyConfig:
    p = Path(path)
    if not p.exists():
        return default_config()

    with open(p) as f:
        raw = yaml.safe_load(f) or {}

    screen = raw.get("screen", {})
    player = raw.get("player", {})
    pc = player.get("color", [255, 255, 0])
    if isinstance(pc, list):
        pc = tuple(pc[:3])

    return FlappyConfig(
        name=raw.get("name", "flappy"),
        screen_width=screen.get("width", 800),
        screen_height=screen.get("height", 600),
        fps=screen.get("fps", 60),
        player_color=pc,
        difficulty=raw.get("difficulty", {}),
    )


def default_config() -> FlappyConfig:
    return FlappyConfig(
        difficulty={
            "easy": {"gravity": 0.3, "flap_impulse": -8, "pipe_speed": 2, "pipe_gap": 220, "spawn_interval": 90, "grace_period": 120},
            "normal": {"gravity": 0.5, "flap_impulse": -10, "pipe_speed": 3, "pipe_gap": 180, "spawn_interval": 70, "grace_period": 90},
            "hard": {"gravity": 0.7, "flap_impulse": -13, "pipe_speed": 5, "pipe_gap": 140, "spawn_interval": 50, "grace_period": 60},
        }
    )
