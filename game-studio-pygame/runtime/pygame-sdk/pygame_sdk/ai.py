"""AI behavior system for enemy entities."""
from __future__ import annotations

import math
from enum import IntEnum
from typing import TYPE_CHECKING

from .vector import Vector2D

if TYPE_CHECKING:
    from .entity import Entity
    from .pathfind import PathFinder
    from .world import TileMap


class BehaviorType(IntEnum):
    IDLE = 0
    PATROL = 1
    CHASE = 2
    FLEE = 3
    WANDER = 4


class AIAgent:
    """Autonomous agent with pluggable behavior for enemy entities."""

    def __init__(self, owner: Entity) -> None:
        self.owner: Entity = owner
        self.behavior: BehaviorType = BehaviorType.WANDER
        self.target: Entity | None = None
        self.chase_range: float = 10.0
        self.attack_range: float = 1.5
        self.waypoints: list[Vector2D] = []
        self.wander_freq: int = 20
        self._path_finder: PathFinder | None = None
        self._wander_dir: Vector2D = Vector2D()
        self._waypoint_idx: int = 0

    def set_path_finder(self, pf: PathFinder) -> None:
        self._path_finder = pf

    def update(self, tile_map: TileMap | None, frame: int) -> None:
        """Run one AI update tick."""
        if self.target is None or not self.target.active:
            self.behavior = BehaviorType.WANDER

        if self.behavior == BehaviorType.IDLE:
            pass
        elif self.behavior == BehaviorType.PATROL:
            self._update_patrol()
        elif self.behavior == BehaviorType.CHASE:
            self._update_chase(tile_map)
        elif self.behavior == BehaviorType.FLEE:
            self._update_flee()
        elif self.behavior == BehaviorType.WANDER:
            self._update_wander(frame, tile_map)

        # Auto-transition based on target distance
        if self.target is not None and self.target.active:
            dist = self.owner.pos.distance_to(self.target.pos)
            if dist <= self.chase_range and dist > self.attack_range:
                self.behavior = BehaviorType.CHASE
            elif dist <= self.attack_range:
                self.behavior = BehaviorType.IDLE

    def _update_chase(self, tile_map: TileMap | None) -> None:
        if self.target is None:
            return
        if self._path_finder is not None and tile_map is not None:
            next_pos = self._path_finder.next_step(self.owner.pos, self.target.pos)
            self.owner.pos = next_pos
        else:
            dir_vec = self.target.pos.sub(self.owner.pos).normalize()
            self.owner.pos = self.owner.pos.add(dir_vec.scale(self.owner.vel.length()))

    def _update_flee(self) -> None:
        if self.target is None:
            return
        dir_vec = self.owner.pos.sub(self.target.pos).normalize()
        self.owner.pos = self.owner.pos.add(dir_vec.scale(self.owner.vel.length()))

    def _update_patrol(self) -> None:
        if not self.waypoints:
            return
        target = self.waypoints[self._waypoint_idx]
        dir_vec = target.sub(self.owner.pos)
        if dir_vec.length() < 1:
            self._waypoint_idx = (self._waypoint_idx + 1) % len(self.waypoints)
            return
        self.owner.pos = self.owner.pos.add(dir_vec.normalize().scale(self.owner.vel.length()))

    def _update_wander(self, frame: int, tile_map: TileMap | None) -> None:
        if frame % self.wander_freq == 0:
            angle = float(frame % 360) * 0.1
            self._wander_dir = Vector2D(math.cos(angle), math.sin(angle))
        new_pos = self.owner.pos.add(self._wander_dir.scale(0.5))
        if tile_map is not None:
            nx = round(new_pos.x)
            ny = round(new_pos.y)
            if tile_map.is_walkable(nx, ny):
                self.owner.pos = new_pos
            else:
                self._wander_dir = self._wander_dir.scale(-1)
        else:
            self.owner.pos = new_pos
