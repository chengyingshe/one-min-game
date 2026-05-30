"""Spatial hash for broad-phase collision detection."""
from __future__ import annotations

from .collision import Rect, overlaps
from .entity import Entity, EntityStore


class SpatialHash:
    """Grid-based spatial partitioning for efficient proximity queries."""

    def __init__(self, cell_size: float, store: EntityStore) -> None:
        self._cell_size = cell_size
        self._store = store
        self._cells: dict[tuple[int, int], list[int]] = {}

    def _cell_key(self, x: float, y: float) -> tuple[int, int]:
        return (int(x / self._cell_size), int(y / self._cell_size))

    def update(self) -> None:
        """Rebuild spatial hash from entity store."""
        self._cells.clear()
        for e in self._store.get_active():
            key = self._cell_key(e.pos.x, e.pos.y)
            self._cells.setdefault(key, []).append(e.id)

    def query(self, region: Rect) -> list[Entity]:
        """Return all entities whose bounds overlap the query region."""
        result: list[Entity] = []
        min_cx = int(region.x / self._cell_size)
        min_cy = int(region.y / self._cell_size)
        max_cx = int((region.x + region.w) / self._cell_size)
        max_cy = int((region.y + region.h) / self._cell_size)

        seen: set[int] = set()
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                for eid in self._cells.get((cx, cy), []):
                    if eid not in seen:
                        seen.add(eid)
                        e, found = self._store.get(eid)
                        if found and e is not None:
                            if overlaps(e.bounds(), region):
                                result.append(e)
        return result

    def query_nearby(self, entity: Entity) -> list[Entity]:
        """Return all entities in cells adjacent to the given entity."""
        r = entity.bounds()
        margin = self._cell_size
        region = Rect(
            x=r.x - margin,
            y=r.y - margin,
            w=r.w + margin * 2,
            h=r.h + margin * 2,
        )
        return self.query(region)
