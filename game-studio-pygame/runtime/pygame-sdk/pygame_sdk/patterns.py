"""Movement patterns: Protocol and implementations for entity movement."""
from __future__ import annotations

import math
from typing import Protocol, runtime_checkable

from .vector import Vector2D


@runtime_checkable
class MovementPattern(Protocol):
    """Protocol for entity movement patterns."""

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None: ...
    def reset(self) -> None: ...


class LinearPattern:
    """Move in a fixed direction at constant speed."""

    def __init__(self, direction: Vector2D, speed: float) -> None:
        self.direction = direction
        self.speed = speed

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        dir_norm = self.direction.normalize()
        new_pos = pos.add(dir_norm.scale(self.speed))
        pos.x = new_pos.x
        pos.y = new_pos.y
        vel.x = dir_norm.x * self.speed
        vel.y = dir_norm.y * self.speed

    def reset(self) -> None:
        pass


class SinusoidalPattern:
    """Oscillate along an axis with configurable amplitude and frequency."""

    def __init__(
        self,
        axis: Vector2D,
        amplitude: float,
        frequency: float,
        base_offset: Vector2D | None = None,
    ) -> None:
        self.axis = axis
        self.amplitude = amplitude
        self.frequency = frequency
        self.base_offset = base_offset if base_offset is not None else Vector2D()

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        t = float(frame) * self.frequency
        offset = self.axis.normalize().scale(self.amplitude * math.sin(t))
        new_pos = pos.add(self.base_offset).add(offset)
        pos.x = new_pos.x
        pos.y = new_pos.y

    def reset(self) -> None:
        pass


class HomingPattern:
    """Gradually steer towards a target entity."""

    def __init__(
        self,
        target_entity: "Entity | None",
        speed: float,
        turn_rate: float,
    ) -> None:
        self.target = target_entity
        self.speed = speed
        self.turn_rate = turn_rate

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        if self.target is None or not self.target.active:
            return
        from .entity import Entity

        dir_to_target = self.target.pos.sub(pos).normalize()
        current = vel.normalize()
        blended = current.add(dir_to_target.scale(self.turn_rate)).normalize()
        vel.x = blended.x * self.speed
        vel.y = blended.y * self.speed
        new_pos = pos.add(vel)
        pos.x = new_pos.x
        pos.y = new_pos.y

    def reset(self) -> None:
        pass


class OrbitPattern:
    """Circle around a center point."""

    def __init__(self, center: Vector2D, radius: float, angular_speed: float) -> None:
        self.center = center
        self.radius = radius
        self.angular_speed = angular_speed

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        angle = float(frame) * self.angular_speed
        pos.x = self.center.x + self.radius * math.cos(angle)
        pos.y = self.center.y + self.radius * math.sin(angle)

    def reset(self) -> None:
        pass


class GridPattern:
    """Move by fixed integer steps on a grid."""

    def __init__(self, dx: int, dy: int) -> None:
        self.dx = dx
        self.dy = dy

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        pos.x += float(self.dx)
        pos.y += float(self.dy)

    def reset(self) -> None:
        pass


class PatrolPattern:
    """Cycle through a list of waypoints."""

    def __init__(self, points: list[Vector2D], speed: float) -> None:
        self.points = points
        self.speed = speed
        self._index: int = 0

    def update(self, pos: Vector2D, vel: Vector2D, frame: int) -> None:
        if not self.points:
            return
        target = self.points[self._index]
        dir_vec = target.sub(pos)
        dist = dir_vec.length()
        if dist < self.speed:
            pos.x = target.x
            pos.y = target.y
            self._index = (self._index + 1) % len(self.points)
        else:
            norm = dir_vec.normalize().scale(self.speed)
            new_pos = pos.add(norm)
            pos.x = new_pos.x
            pos.y = new_pos.y
        vel_norm = dir_vec.normalize().scale(self.speed)
        vel.x = vel_norm.x
        vel.y = vel_norm.y

    def reset(self) -> None:
        self._index = 0


def update_pattern(entity: "Entity", frame: int) -> None:
    """Apply entity's movement pattern if it has one."""
    if entity.pattern is not None:
        entity.pattern.update(entity.pos, entity.vel, frame)
