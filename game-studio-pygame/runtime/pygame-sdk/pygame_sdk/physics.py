"""Physics helpers: gravity, velocity, position clamping."""
from __future__ import annotations

from .entity import Entity
from .vector import Vector2D


def apply_gravity(entity: Entity, gravity: float) -> None:
    """Apply gravity to entity Y velocity and integrate position."""
    entity.vel.y += gravity
    entity.pos.y += entity.vel.y
    if entity.pos.y < 0:
        entity.pos.y = 0
        entity.vel.y = 0


def apply_velocity(entity: Entity) -> None:
    """Integrate velocity into position."""
    entity.pos = entity.pos.add(entity.vel)


def set_velocity(entity: Entity, vx: float, vy: float) -> None:
    """Set entity velocity components directly."""
    entity.vel = Vector2D(vx, vy)


def set_velocity_y(entity: Entity, vy: float) -> None:
    """Set only the Y component of velocity."""
    entity.vel.y = vy


def clamp_position(
    entity: Entity,
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> None:
    """Clamp entity position within rectangular bounds."""
    if entity.pos.x < min_x:
        entity.pos.x = min_x
    if entity.pos.y < min_y:
        entity.pos.y = min_y
    if entity.pos.x > max_x:
        entity.pos.x = max_x
    if entity.pos.y > max_y:
        entity.pos.y = max_y
