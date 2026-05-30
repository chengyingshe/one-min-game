"""Procedural world generation for Wild Survivors."""
from __future__ import annotations

import random

from pygame_sdk import Entity, EntityType, Vector2D

# Resource type markers
TREE = "tree"
ROCK = "rock"
ORE = "ore"


def generate_world(
    world_w: int,
    world_h: int,
    tile_size: int,
    resources_config: dict,
    seed: int | None = None,
) -> tuple[list[list[int]], list[Entity]]:
    """Generate the tile map and resource entities.

    Returns:
        (tile_grid, resource_entities)
        tile_grid: 2D list, 0=walkable grass, 1=blocked (resource occupies)
    """
    if seed is not None:
        random.seed(seed)

    tile_grid = [[0] * world_w for _ in range(world_h)]
    entities: list[Entity] = []

    # Spawn clearing: keep center 12x10 tiles empty
    cx, cy = world_w // 2, world_h // 2
    clear_half_w, clear_half_h = 6, 5

    def in_clearing(tx: int, ty: int) -> bool:
        return abs(tx - cx) < clear_half_w and abs(ty - cy) < clear_half_h

    def place_resource(etype: str, tx: int, ty: int) -> None:
        cfg = resources_config.get(etype)
        if cfg is None:
            return
        pixel_x = tx * tile_size
        pixel_y = ty * tile_size
        e = Entity(
            type=EntityType.RESOURCE,
            symbol="T" if etype == TREE else ("R" if etype == ROCK else "O"),
            pos=Vector2D(float(pixel_x), float(pixel_y)),
            size=Vector2D(float(tile_size), float(tile_size)),
            hp=cfg.hp,
            max_hp=cfg.hp,
            color=cfg.color,
            tags={"resource_type": etype, "drop": cfg.drop},
        )
        entities.append(e)
        tile_grid[ty][tx] = 1

    # Place tree clusters (most common)
    for _ in range(35):
        bx = random.randint(2, world_w - 3)
        by = random.randint(2, world_h - 3)
        for dx in range(random.randint(2, 5)):
            for dy in range(random.randint(2, 4)):
                tx, ty = bx + dx, by + dy
                if (0 <= tx < world_w and 0 <= ty < world_h
                        and tile_grid[ty][tx] == 0
                        and not in_clearing(tx, ty)
                        and random.random() < 0.6):
                    place_resource(TREE, tx, ty)

    # Place rock formations
    for _ in range(15):
        bx = random.randint(2, world_w - 3)
        by = random.randint(2, world_h - 3)
        for dx in range(random.randint(1, 3)):
            for dy in range(random.randint(1, 2)):
                tx, ty = bx + dx, by + dy
                if (0 <= tx < world_w and 0 <= ty < world_h
                        and tile_grid[ty][tx] == 0
                        and not in_clearing(tx, ty)
                        and random.random() < 0.5):
                    place_resource(ROCK, tx, ty)

    # Place ore deposits (rarest)
    for _ in range(8):
        bx = random.randint(3, world_w - 4)
        by = random.randint(3, world_h - 4)
        for dx in range(random.randint(1, 2)):
            for dy in range(random.randint(1, 2)):
                tx, ty = bx + dx, by + dy
                if (0 <= tx < world_w and 0 <= ty < world_h
                        and tile_grid[ty][tx] == 0
                        and not in_clearing(tx, ty)
                        and random.random() < 0.4):
                    place_resource(ORE, tx, ty)

    return tile_grid, entities
