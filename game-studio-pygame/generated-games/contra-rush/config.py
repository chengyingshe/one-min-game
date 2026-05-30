from __future__ import annotations

import os
from dataclasses import dataclass, field

import yaml


@dataclass
class ContraConfig:
    name: str = "Contra Rush"
    screen_width: int = 800
    screen_height: int = 608
    fps: int = 60
    player_hp: int = 3
    player_color: tuple = (0, 200, 50)
    player_size: tuple = (24, 32)
    player_speed: float = 4.0
    bullet_speed: float = 7.0
    bullet_size: tuple = (8, 4)
    bullet_color: tuple = (255, 255, 0)
    shoot_cooldown: int = 15
    jump_impulse: float = -12.0
    gravity: float = 0.6
    soldier_color: tuple = (200, 50, 50)
    soldier_size: tuple = (24, 32)
    turret_color: tuple = (150, 30, 30)
    turret_size: tuple = (24, 24)
    drone_color: tuple = (150, 150, 150)
    drone_size: tuple = (20, 20)
    enemy_bullet_color: tuple = (255, 150, 0)
    enemy_bullet_size: tuple = (8, 4)
    soldier_hp: int = 1
    turret_hp: int = 2
    drone_hp: int = 1
    health_color: tuple = (255, 100, 150)
    health_size: tuple = (16, 16)
    health_restore: int = 1
    tile_size: int = 32
    level_width: int = 200
    level_height: int = 19
    ground_color: tuple = (100, 70, 40)
    platform_color: tuple = (120, 100, 80)
    bg_color: tuple = (20, 20, 50)
    finish_col: int = 195
    scoring: dict = field(default_factory=lambda: {
        "soldier": 10, "turret": 25, "drone": 15,
        "finish": 100, "health_bonus": 20,
    })
    difficulty: dict = field(default_factory=lambda: {
        "easy": {"player_hp": 5, "player_speed": 5, "player_bullet_speed": 8,
                 "enemy_speed": 1.5, "enemy_shoot_rate": 120, "grace_period": 180},
        "normal": {"player_hp": 3, "player_speed": 4, "player_bullet_speed": 7,
                   "enemy_speed": 2.5, "enemy_shoot_rate": 80, "grace_period": 120},
        "hard": {"player_hp": 2, "player_speed": 4, "player_bullet_speed": 6,
                 "enemy_speed": 3.5, "enemy_shoot_rate": 50, "grace_period": 60},
    })

    def params(self, tier: str) -> dict:
        return self.difficulty.get(tier, self.difficulty["normal"])


def _tuple(v) -> tuple:
    if isinstance(v, list):
        return tuple(v)
    return v


def load_config(path: str | None = None) -> ContraConfig:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "config.yaml")
    cfg = ContraConfig()
    if not os.path.exists(path):
        return cfg
    with open(path) as f:
        d = yaml.safe_load(f) or {}
    scr = d.get("screen", {})
    cfg.screen_width = scr.get("width", cfg.screen_width)
    cfg.screen_height = scr.get("height", cfg.screen_height)
    cfg.fps = scr.get("fps", cfg.fps)
    p = d.get("player", {})
    cfg.player_hp = p.get("hp", cfg.player_hp)
    cfg.player_color = _tuple(p.get("color", cfg.player_color))
    cfg.player_size = _tuple(p.get("size", cfg.player_size))
    cfg.player_speed = float(p.get("speed", cfg.player_speed))
    cfg.bullet_speed = float(p.get("bullet_speed", cfg.bullet_speed))
    cfg.bullet_size = _tuple(p.get("bullet_size", cfg.bullet_size))
    cfg.bullet_color = _tuple(p.get("bullet_color", cfg.bullet_color))
    cfg.shoot_cooldown = p.get("shoot_cooldown", cfg.shoot_cooldown)
    cfg.jump_impulse = float(p.get("jump_impulse", cfg.jump_impulse))
    cfg.gravity = float(p.get("gravity", cfg.gravity))
    e = d.get("enemy", {})
    cfg.soldier_color = _tuple(e.get("soldier_color", cfg.soldier_color))
    cfg.soldier_size = _tuple(e.get("soldier_size", cfg.soldier_size))
    cfg.turret_color = _tuple(e.get("turret_color", cfg.turret_color))
    cfg.turret_size = _tuple(e.get("turret_size", cfg.turret_size))
    cfg.drone_color = _tuple(e.get("drone_color", cfg.drone_color))
    cfg.drone_size = _tuple(e.get("drone_size", cfg.drone_size))
    cfg.enemy_bullet_color = _tuple(e.get("bullet_color", cfg.enemy_bullet_color))
    cfg.enemy_bullet_size = _tuple(e.get("bullet_size", cfg.enemy_bullet_size))
    cfg.soldier_hp = e.get("soldier_hp", cfg.soldier_hp)
    cfg.turret_hp = e.get("turret_hp", cfg.turret_hp)
    cfg.drone_hp = e.get("drone_hp", cfg.drone_hp)
    pk = d.get("pickup", {})
    cfg.health_color = _tuple(pk.get("health_color", cfg.health_color))
    cfg.health_size = _tuple(pk.get("health_size", cfg.health_size))
    cfg.health_restore = pk.get("health_restore", cfg.health_restore)
    lv = d.get("level", {})
    cfg.tile_size = lv.get("tile_size", cfg.tile_size)
    cfg.level_width = lv.get("width", cfg.level_width)
    cfg.level_height = lv.get("height", cfg.level_height)
    cfg.ground_color = _tuple(lv.get("ground_color", cfg.ground_color))
    cfg.platform_color = _tuple(lv.get("platform_color", cfg.platform_color))
    cfg.bg_color = _tuple(lv.get("bg_color", cfg.bg_color))
    cfg.finish_col = lv.get("finish_col", cfg.finish_col)
    cfg.scoring = d.get("scoring", cfg.scoring)
    cfg.difficulty = d.get("difficulty", cfg.difficulty)
    return cfg
