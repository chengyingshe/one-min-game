"""Force accumulation and drag for physics simulation."""
from __future__ import annotations

from dataclasses import dataclass, field

from .entity import Entity
from .vector import Vector2D


@dataclass
class Force:
    """A force vector applied over a number of frames."""

    vector: Vector2D
    duration: int = 1


class ForceAccumulator:
    """Collects forces and resolves them into velocity changes."""

    def __init__(self) -> None:
        self._forces: list[Force] = []

    def add(self, force: Force) -> None:
        self._forces.append(force)

    def resolve(self, entity: Entity) -> None:
        """Apply accumulated forces to entity velocity. Decays durations."""
        total = Vector2D()
        remaining: list[Force] = []
        for f in self._forces:
            total = total.add(f.vector)
            if f.duration > 1:
                remaining.append(Force(vector=f.vector, duration=f.duration - 1))
        if entity.material.mass > 0:
            entity.vel = entity.vel.add(total.scale(1.0 / entity.material.mass))
        self._forces = remaining

    def clear(self) -> None:
        self._forces.clear()


def apply_gravity_2d(entity: Entity, gravity: Vector2D) -> None:
    """Apply directional gravity (not just downward) to entity."""
    if entity.material.mass > 0:
        entity.vel = entity.vel.add(gravity)


def apply_drag(entity: Entity, coefficient: float) -> None:
    """Apply velocity drag (0..1). Higher = more drag."""
    entity.vel = entity.vel.scale(1.0 - coefficient)
