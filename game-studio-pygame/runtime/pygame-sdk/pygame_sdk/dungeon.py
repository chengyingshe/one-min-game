"""Procedural dungeon generation."""
from __future__ import annotations

import random
from dataclasses import dataclass

from .world import TileMap, TileType


@dataclass
class DungeonConfig:
    """Parameters for dungeon generation."""

    width: int = 40
    height: int = 30
    min_room_size: int = 3
    max_room_size: int = 8
    max_rooms: int = 8
    wall_symbol: str = "#"
    floor_symbol: str = "."
    wall_color: tuple[int, int, int] = (100, 100, 100)
    floor_color: tuple[int, int, int] = (60, 50, 40)
    corridor_color: tuple[int, int, int] = (50, 45, 35)
    seed: int | None = None


def generate_dungeon(config: DungeonConfig | None = None) -> TileMap:
    """Generate a random dungeon as a TileMap.

    Uses BSP-style room placement with corridor connections.
    """
    if config is None:
        config = DungeonConfig()

    rng = random.Random(config.seed)
    tile_map = TileMap(config.width, config.height)

    # Fill with walls
    wall_tile = TileType(
        symbol=config.wall_symbol,
        walkable=False,
        solid=True,
        color=config.wall_color,
    )
    for y in range(config.height):
        for x in range(config.width):
            tile_map.tiles[y][x] = TileType(
                symbol=wall_tile.symbol,
                walkable=wall_tile.walkable,
                solid=wall_tile.solid,
                color=wall_tile.color,
            )

    floor_tile = TileType(
        symbol=config.floor_symbol,
        walkable=True,
        solid=False,
        color=config.floor_color,
    )

    rooms: list[tuple[int, int, int, int]] = []  # (x, y, w, h)

    for _ in range(config.max_rooms * 3):
        if len(rooms) >= config.max_rooms:
            break

        w = rng.randint(config.min_room_size, config.max_room_size)
        h = rng.randint(config.min_room_size, config.max_room_size)
        x = rng.randint(1, config.width - w - 1)
        y = rng.randint(1, config.height - h - 1)

        new_room = (x, y, w, h)

        # Check overlap with existing rooms (with 1-tile margin)
        overlap = False
        for rx, ry, rw, rh in rooms:
            if (
                x < rx + rw + 1
                and x + w + 1 > rx
                and y < ry + rh + 1
                and y + h + 1 > ry
            ):
                overlap = True
                break

        if not overlap:
            rooms.append(new_room)
            # Carve room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    tile_map.tiles[ry][rx] = TileType(
                        symbol=floor_tile.symbol,
                        walkable=floor_tile.walkable,
                        solid=floor_tile.solid,
                        color=floor_tile.color,
                    )

    # Connect rooms with corridors
    corridor_tile = TileType(
        symbol=config.floor_symbol,
        walkable=True,
        solid=False,
        color=config.corridor_color,
    )

    for i in range(1, len(rooms)):
        x1 = rooms[i - 1][0] + rooms[i - 1][2] // 2
        y1 = rooms[i - 1][1] + rooms[i - 1][3] // 2
        x2 = rooms[i][0] + rooms[i][2] // 2
        y2 = rooms[i][1] + rooms[i][3] // 2

        # L-shaped corridor: horizontal then vertical
        cx = x1
        while cx != x2:
            if 0 <= cx < config.width and 0 <= y1 < config.height:
                tile_map.tiles[y1][cx] = TileType(
                    symbol=corridor_tile.symbol,
                    walkable=corridor_tile.walkable,
                    solid=corridor_tile.solid,
                    color=corridor_tile.color,
                )
            cx += 1 if x2 > x1 else -1

        cy = y1
        while cy != y2:
            if 0 <= x2 < config.width and 0 <= cy < config.height:
                tile_map.tiles[cy][x2] = TileType(
                    symbol=corridor_tile.symbol,
                    walkable=corridor_tile.walkable,
                    solid=corridor_tile.solid,
                    color=corridor_tile.color,
                )
            cy += 1 if y2 > y1 else -1

    return tile_map
