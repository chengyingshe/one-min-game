"""Collision detection: AABB overlap, bounds checking, pair detection, resolution."""
from __future__ import annotations

from dataclasses import dataclass

from .entity import Entity
from .vector import Vector2D


@dataclass
class Rect:
    """Axis-aligned bounding rectangle."""

    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0


def overlaps(a: Rect, b: Rect) -> bool:
    """Test if two rectangles overlap (AABB)."""
    return (
        a.x < b.x + b.w
        and a.x + a.w > b.x
        and a.y < b.y + b.h
        and a.y + a.h > b.y
    )


def hit_bounds(entity: Entity, width: float, height: float) -> bool:
    """Check if entity is outside the play area."""
    return (
        entity.pos.y >= height
        or entity.pos.y < 0
        or entity.pos.x < 0
        or entity.pos.x >= width
    )


def hit_ground(entity: Entity, height: int) -> bool:
    """Check if entity has reached the ground (height - 2 for UI margin)."""
    play_height = float(height - 2)
    return entity.pos.y >= play_height


def check_collision_pairs(entities: list[Entity]) -> list[list[int]]:
    """Return all colliding entity ID pairs as [[id_a, id_b], ...]."""
    pairs: list[list[int]] = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            if overlaps(entities[i].bounds(), entities[j].bounds()):
                pairs.append([entities[i].id, entities[j].id])
    return pairs


@dataclass
class CollisionPair:
    """Detailed collision info between two entities."""

    a: Entity
    b: Entity
    normal: Vector2D
    depth: float


def check_layered_collisions(entities: list[Entity]) -> list[CollisionPair]:
    """Check collisions respecting collision_layer / collision_mask bitmasks."""
    pairs: list[CollisionPair] = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            a, b = entities[i], entities[j]
            # Both must have at least one matching layer/mask bit
            if (a.collision_layer & b.collision_mask == 0) and (
                b.collision_layer & a.collision_mask == 0
            ):
                continue
            if overlaps(a.bounds(), b.bounds()):
                normal, depth = _compute_collision_normal(a, b)
                pairs.append(CollisionPair(a=a, b=b, normal=normal, depth=depth))
    return pairs


def _compute_collision_normal(a: Entity, b: Entity) -> tuple[Vector2D, float]:
    """Compute collision normal and penetration depth between two entities."""
    a_r, b_r = a.bounds(), b.bounds()
    overlap_x = min(a_r.x + a_r.w, b_r.x + b_r.w) - max(a_r.x, b_r.x)
    overlap_y = min(a_r.y + a_r.h, b_r.y + b_r.h) - max(a_r.y, b_r.y)
    center_a = Vector2D(a_r.x + a_r.w / 2, a_r.y + a_r.h / 2)
    center_b = Vector2D(b_r.x + b_r.w / 2, b_r.y + b_r.h / 2)
    diff = center_b.sub(center_a)
    if overlap_x < overlap_y:
        depth = overlap_x
        if diff.x > 0:
            return Vector2D(1, 0), depth
        return Vector2D(-1, 0), depth
    depth = overlap_y
    if diff.y > 0:
        return Vector2D(0, 1), depth
    return Vector2D(0, -1), depth


def resolve_collision(pair: CollisionPair) -> None:
    """Apply impulse-based collision response."""
    rel_vel = pair.b.vel.sub(pair.a.vel)
    vel_along_normal = rel_vel.dot(pair.normal)
    if vel_along_normal > 0:
        return

    e = min(pair.a.material.restitution, pair.b.material.restitution)
    inv_mass_a = 0.0
    if pair.a.material.mass > 0:
        inv_mass_a = 1.0 / pair.a.material.mass
    inv_mass_b = 0.0
    if pair.b.material.mass > 0:
        inv_mass_b = 1.0 / pair.b.material.mass
    if inv_mass_a + inv_mass_b == 0:
        return

    j = -(1 + e) * vel_along_normal / (inv_mass_a + inv_mass_b)
    impulse = pair.normal.scale(j)
    if pair.a.material.mass > 0:
        pair.a.vel = pair.a.vel.sub(impulse.scale(inv_mass_a))
    if pair.b.material.mass > 0:
        pair.b.vel = pair.b.vel.add(impulse.scale(inv_mass_b))
    separate_entities(pair)


def separate_entities(pair: CollisionPair) -> None:
    """Push overlapping entities apart proportional to inverse mass."""
    inv_mass_a = 0.0
    if pair.a.material.mass > 0:
        inv_mass_a = 1.0 / pair.a.material.mass
    inv_mass_b = 0.0
    if pair.b.material.mass > 0:
        inv_mass_b = 1.0 / pair.b.material.mass
    total = inv_mass_a + inv_mass_b
    if total == 0:
        return
    correction = pair.normal.scale(pair.depth / total)
    if pair.a.material.mass > 0:
        pair.a.pos = pair.a.pos.sub(correction.scale(inv_mass_a))
    if pair.b.material.mass > 0:
        pair.b.pos = pair.b.pos.add(correction.scale(inv_mass_b))


def bounce_velocity(vel: Vector2D, normal: Vector2D, restitution: float) -> Vector2D:
    """Reflect velocity off a surface with restitution."""
    return vel.reflect(normal).scale(restitution)


def slide_velocity(vel: Vector2D, normal: Vector2D, friction: float) -> Vector2D:
    """Slide along a surface with friction."""
    dot = vel.dot(normal)
    tangent = vel.sub(normal.scale(dot))
    return tangent.scale(1.0 - friction)
