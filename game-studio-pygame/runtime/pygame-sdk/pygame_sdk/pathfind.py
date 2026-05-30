"""A* pathfinding on a TileMap."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .vector import Vector2D
from .world import TileMap


@dataclass
class _PathNode:
    x: int
    y: int
    g: float
    h: float
    f: float
    parent_x: int
    parent_y: int


# 8-directional movement deltas
_DIRS: list[tuple[int, int]] = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
]


def _heuristic(x1: int, y1: int, x2: int, y2: int) -> float:
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if dx > dy:
        return dx + dy * 0.414
    return dy + dx * 0.414


class PathFinder:
    """A* pathfinding on a TileMap grid."""

    def __init__(self, tile_map: TileMap) -> None:
        self.tile_map = tile_map

    def find_path(self, start: Vector2D, goal: Vector2D) -> list[Vector2D]:
        """Find a path from start to goal. Returns empty list if no path."""
        sx = round(start.x)
        sy = round(start.y)
        ex = round(goal.x)
        ey = round(goal.y)

        if not self.tile_map.is_walkable(ex, ey) or not self.tile_map.is_walkable(sx, sy):
            return []

        open_set: dict[tuple[int, int], _PathNode] = {}
        closed_set: set[tuple[int, int]] = set()

        h = _heuristic(sx, sy, ex, ey)
        start_node = _PathNode(x=sx, y=sy, g=0.0, h=h, f=h, parent_x=sx, parent_y=sy)
        open_set[(sx, sy)] = start_node

        while open_set:
            # Find lowest f-score node
            current_key = min(open_set, key=lambda k: open_set[k].f)
            current = open_set[current_key]

            if current.x == ex and current.y == ey:
                # Reconstruct path
                path: list[Vector2D] = []
                while current.x != sx or current.y != sy:
                    path.insert(0, Vector2D(float(current.x), float(current.y)))
                    parent_key = (current.parent_x, current.parent_y)
                    parent = open_set.get(parent_key)
                    if parent is None:
                        break
                    current = parent
                return path

            del open_set[current_key]
            closed_set.add(current_key)

            for dx, dy in _DIRS:
                nx, ny = current.x + dx, current.y + dy
                if not self.tile_map.is_walkable(nx, ny):
                    continue
                nk = (nx, ny)
                if nk in closed_set:
                    continue

                cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                g = current.g + cost
                h_val = _heuristic(nx, ny, ex, ey)

                existing = open_set.get(nk)
                if existing is not None and g >= existing.g:
                    continue

                open_set[nk] = _PathNode(
                    x=nx,
                    y=ny,
                    g=g,
                    h=h_val,
                    f=g + h_val,
                    parent_x=current.x,
                    parent_y=current.y,
                )

        return []

    def next_step(self, start: Vector2D, goal: Vector2D) -> Vector2D:
        """Return the next step toward goal, or start if no path."""
        path = self.find_path(start, goal)
        if not path:
            return start
        return path[0]

    def random_walkable(self) -> Vector2D:
        """Return the first walkable tile position (scans top-to-bottom)."""
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                if self.tile_map.is_walkable(x, y):
                    return Vector2D(float(x), float(y))
        return Vector2D()
