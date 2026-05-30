"""Config loader for Wild Survivors."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ResourceDef:
    name: str = ""
    hp: int = 3
    color: tuple[int, int, int] = (128, 128, 128)
    drop: str = "wood"


@dataclass
class EnemyDef:
    name: str = ""
    hp: int = 3
    damage: int = 1
    speed: float = 40.0
    color: tuple[int, int, int] = (128, 128, 128)
    spawn_rate: float = 0.02


@dataclass
class StructureDef:
    name: str = ""
    hp: int = 15
    cost_wood: int = 0
    cost_stone: int = 0
    cost_iron: int = 0
    color: tuple[int, int, int] = (128, 128, 128)


@dataclass
class DifficultyDef:
    tier: str = "normal"
    enemy_speed: float = 50.0
    spawn_rate: int = 150
    player_hp: int = 10
    grace_period: int = 180


@dataclass
class WildSurvivorsConfig:
    name: str = "wild-survivors"
    screen_width: int = 800
    screen_height: int = 600
    fps: int = 60
    player_hp: int = 10
    player_speed: float = 150.0
    world_width: int = 80
    world_height: int = 60
    tile_size: int = 16
    duration: int = 120
    controls: str = ""
    resources: dict[str, ResourceDef] = field(default_factory=dict)
    enemies: dict[str, EnemyDef] = field(default_factory=dict)
    structures: dict[str, StructureDef] = field(default_factory=dict)
    difficulty: dict[str, DifficultyDef] = field(default_factory=dict)
    multiplayer_enabled: bool = True
    max_players: int = 4
    shared_viewport: bool = True


def _tuple_color(val: Any) -> tuple[int, int, int]:
    if isinstance(val, (list, tuple)) and len(val) >= 3:
        return (int(val[0]), int(val[1]), int(val[2]))
    return (128, 128, 128)


def load_config(path: str | Path | None = None) -> WildSurvivorsConfig:
    if path is None:
        path = Path(__file__).parent / "config.yaml"

    path = Path(path)
    if not path.exists():
        return WildSurvivorsConfig()

    with open(path) as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    screen = raw.get("screen", {})
    player = raw.get("player", {})
    world = raw.get("world", {})
    gameplay = raw.get("gameplay", {})
    mp = raw.get("multiplayer", {})

    resources: dict[str, ResourceDef] = {}
    for rname, rdata in raw.get("resources", {}).items():
        if isinstance(rdata, dict):
            resources[rname] = ResourceDef(
                name=rname,
                hp=rdata.get("hp", 3),
                color=_tuple_color(rdata.get("color")),
                drop=rdata.get("drop", "wood"),
            )

    enemies: dict[str, EnemyDef] = {}
    for ename, edata in raw.get("enemies", {}).items():
        if isinstance(edata, dict):
            enemies[ename] = EnemyDef(
                name=ename,
                hp=edata.get("hp", 3),
                damage=edata.get("damage", 1),
                speed=float(edata.get("speed", 40)),
                color=_tuple_color(edata.get("color")),
                spawn_rate=float(edata.get("spawn_rate", 0.02)),
            )

    structures: dict[str, StructureDef] = {}
    for sname, sdata in raw.get("structures", {}).items():
        if isinstance(sdata, dict):
            structures[sname] = StructureDef(
                name=sname,
                hp=sdata.get("hp", 15),
                cost_wood=sdata.get("cost_wood", 0),
                cost_stone=sdata.get("cost_stone", 0),
                cost_iron=sdata.get("cost_iron", 0),
                color=_tuple_color(sdata.get("color")),
            )

    difficulty: dict[str, DifficultyDef] = {}
    for dname, ddata in raw.get("difficulty", {}).items():
        if isinstance(ddata, dict):
            difficulty[dname] = DifficultyDef(
                tier=dname,
                enemy_speed=float(ddata.get("enemy_speed", 50)),
                spawn_rate=int(ddata.get("spawn_rate", 150)),
                player_hp=int(ddata.get("player_hp", 10)),
                grace_period=int(ddata.get("grace_period", 180)),
            )

    return WildSurvivorsConfig(
        name=raw.get("name", "wild-survivors"),
        screen_width=screen.get("width", 800),
        screen_height=screen.get("height", 600),
        fps=screen.get("fps", 60),
        player_hp=player.get("hp", 10),
        player_speed=float(player.get("speed", 150.0)),
        world_width=world.get("width", 80),
        world_height=world.get("height", 60),
        tile_size=world.get("tile_size", 16),
        duration=gameplay.get("duration", 120),
        controls=raw.get("controls", ""),
        resources=resources,
        enemies=enemies,
        structures=structures,
        difficulty=difficulty,
        multiplayer_enabled=mp.get("enabled", True),
        max_players=mp.get("max_players", 4),
        shared_viewport=mp.get("shared_viewport", True),
    )
