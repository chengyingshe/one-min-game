"""Entity system: EntityType enum, Entity dataclass, EntityStore class."""
from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Callable

from .material import PhysicsMaterial
from .vector import Vector2D

if TYPE_CHECKING:
    from .collision import Rect
    from .patterns import MovementPattern


class EntityType(IntEnum):
    PLAYER = 0
    ENEMY = 1
    BULLET = 2
    OBSTACLE = 3
    COLLECTIBLE = 4
    RESOURCE = 5
    STRUCTURE = 6


# Type alias for color tuples used by PyGame
Color = tuple[int, int, int]


class Entity:
    """A game entity with position, velocity, size, health, and rendering info.

    Port of Go SDK Entity. Changes from Go:
    - color: (R,G,B) tuple instead of lipgloss style
    - size: pixel dimensions (e.g. 32x32) instead of terminal cells
    - symbol: kept as str for text overlay rendering
    """

    __slots__ = (
        "id",
        "type",
        "symbol",
        "pos",
        "vel",
        "size",
        "hp",
        "max_hp",
        "active",
        "tags",
        "material",
        "collision_layer",
        "collision_mask",
        "color",
        "pattern",
        "owner",
    )

    def __init__(
        self,
        *,
        type: EntityType = EntityType.PLAYER,
        symbol: str = "@",
        pos: Vector2D | None = None,
        vel: Vector2D | None = None,
        size: Vector2D | None = None,
        hp: int = 1,
        max_hp: int = 1,
        active: bool = True,
        tags: dict[str, str] | None = None,
        material: PhysicsMaterial | None = None,
        collision_layer: int = 1,
        collision_mask: int = 0xFFFF,
        color: Color = (255, 255, 255),
        pattern: MovementPattern | None = None,
        owner: str = "",
    ) -> None:
        self.id: int = 0
        self.type: EntityType = type
        self.symbol: str = symbol
        self.pos: Vector2D = pos if pos is not None else Vector2D()
        self.vel: Vector2D = vel if vel is not None else Vector2D()
        self.size: Vector2D = size if size is not None else Vector2D(32, 32)
        self.hp: int = hp
        self.max_hp: int = max_hp if max_hp >= hp else hp
        self.active: bool = active
        self.tags: dict[str, str] = tags if tags is not None else {}
        self.material: PhysicsMaterial = material if material is not None else PhysicsMaterial()
        self.collision_layer: int = collision_layer
        self.collision_mask: int = collision_mask
        self.color: Color = color
        self.pattern: MovementPattern | None = pattern
        self.owner: str = owner

    def bounds(self) -> Rect:
        """Return axis-aligned bounding box."""
        from .collision import Rect

        return Rect(x=self.pos.x, y=self.pos.y, w=self.size.x, h=self.size.y)


class EntityStore:
    """Manages a collection of entities with O(1) lookup by ID."""

    def __init__(self) -> None:
        self._entities: dict[int, Entity] = {}
        self._next_id: int = 1

    def add(self, entity: Entity) -> int:
        """Add entity and return its assigned ID."""
        entity.id = self._next_id
        self._next_id += 1
        self._entities[entity.id] = entity
        return entity.id

    def remove(self, id: int) -> None:
        """Remove entity by ID."""
        self._entities.pop(id, None)

    def get(self, id: int) -> tuple[Entity | None, bool]:
        """Look up entity by ID. Returns (entity, found)."""
        e = self._entities.get(id)
        return e, e is not None

    def get_by_type(self, t: EntityType) -> list[Entity]:
        """Return all active entities of a given type."""
        return [e for e in self._entities.values() if e.type == t and e.active]

    def get_active(self) -> list[Entity]:
        """Return all active entities."""
        return [e for e in self._entities.values() if e.active]

    def update_all(self, fn: Callable[[Entity], None]) -> None:
        """Apply fn to every active entity."""
        for e in self._entities.values():
            if e.active:
                fn(e)

    def count(self) -> int:
        """Total entity count (including inactive)."""
        return len(self._entities)

    def count_by_type(self, t: EntityType) -> int:
        """Count active entities of a given type."""
        return sum(1 for e in self._entities.values() if e.type == t and e.active)

    def clear(self) -> None:
        """Remove all entities."""
        self._entities.clear()
