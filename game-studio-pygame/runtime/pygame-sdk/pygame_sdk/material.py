"""Physics material definitions for collision response."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PhysicsMaterial:
    """Defines how an entity responds to collisions and forces."""

    friction: float = 0.5
    restitution: float = 0.3
    mass: float = 1.0


def default_material() -> PhysicsMaterial:
    return PhysicsMaterial(friction=0.5, restitution=0.3, mass=1.0)


# Preset materials (mirrors Go SDK)
ICE_MATERIAL = PhysicsMaterial(friction=0.05, restitution=0.1, mass=1.0)
RUBBER_MATERIAL = PhysicsMaterial(friction=0.8, restitution=0.9, mass=1.0)
STATIC_MATERIAL = PhysicsMaterial(friction=1.0, restitution=0.0, mass=0.0)
BOUNCY_MATERIAL = PhysicsMaterial(friction=0.3, restitution=0.95, mass=0.5)
HEAVY_MATERIAL = PhysicsMaterial(friction=0.7, restitution=0.1, mass=5.0)
