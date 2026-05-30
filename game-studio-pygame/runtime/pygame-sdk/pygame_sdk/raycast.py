"""Raycast rendering for pseudo-3D / first-person games."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .camera import Camera
from .entity import Entity
from .vector import Vector2D
from .world import TileMap


@dataclass
class RayHit:
    """Result of a single ray cast."""

    distance: float
    tile_type: str
    side: bool
    hit_x: float


class RaycastRenderer:
    """DDA raycast renderer for pseudo-3D rendering on a TileMap.

    Port of Go raycast.go. Renders to a pygame.Surface instead of Buffer.
    """

    def __init__(self, camera: Camera, tile_map: TileMap) -> None:
        self.camera = camera
        self._map_data: list[str] = tile_map.to_string_grid()
        self._map_w: int = tile_map.width
        self._map_h: int = tile_map.height

    def _is_wall(self, mx: int, my: int) -> bool:
        if mx < 0 or mx >= self._map_w or my < 0 or my >= self._map_h:
            return True
        return self._map_data[my][mx] == "#"

    def cast_ray(self, angle: float) -> RayHit:
        """Cast a single ray and return hit information."""
        cam = self.camera
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)
        pos_x = cam.position.x
        pos_y = cam.position.y
        map_x = int(math.floor(pos_x))
        map_y = int(math.floor(pos_y))

        delta_dist_x = abs(1.0 / dir_x) if dir_x != 0 else 1e30
        delta_dist_y = abs(1.0 / dir_y) if dir_y != 0 else 1e30

        if dir_x < 0:
            step_x = -1
            side_dist_x = (pos_x - float(map_x)) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (float(map_x) + 1.0 - pos_x) * delta_dist_x

        if dir_y < 0:
            step_y = -1
            side_dist_y = (pos_y - float(map_y)) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (float(map_y) + 1.0 - pos_y) * delta_dist_y

        side = False
        for _ in range(100):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = False
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = True

            if self._is_wall(map_x, map_y):
                if not side:
                    dist = side_dist_x - delta_dist_x
                else:
                    dist = side_dist_y - delta_dist_y

                if not side:
                    hit_x = pos_y + dist * dir_y
                else:
                    hit_x = pos_x + dist * dir_x
                hit_x -= math.floor(hit_x)

                tile = "#"
                if 0 <= map_x < self._map_w and 0 <= map_y < self._map_h:
                    tile = self._map_data[map_y][map_x]

                return RayHit(distance=dist, tile_type=tile, side=side, hit_x=hit_x)

        return RayHit(distance=100.0, tile_type=" ", side=False, hit_x=0.0)

    def render(self, surface: "pygame.Surface") -> None:
        """Render the raycasted 3D view onto a pygame surface."""
        import pygame

        cam = self.camera
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        for x in range(screen_w):
            camera_x = 2.0 * float(x) / float(screen_w) - 1.0
            ray_angle = cam.direction + cam.fov_angle * camera_x
            hit = self.cast_ray(ray_angle)
            perp_dist = hit.distance * math.cos(ray_angle - cam.direction)
            if perp_dist < 0.01:
                perp_dist = 0.01

            wall_height = int(float(screen_h) / perp_dist)
            draw_start = screen_h // 2 - wall_height // 2
            draw_end = screen_h // 2 + wall_height // 2
            draw_start = max(0, draw_start)
            draw_end = min(screen_h, draw_end)

            # Wall shading based on distance
            if perp_dist < 2:
                shade = 255
            elif perp_dist < 5:
                shade = 180
            elif perp_dist < 10:
                shade = 120
            else:
                shade = 80

            # Side walls are darker
            if hit.side:
                shade = int(shade * 0.7)

            color = (shade, shade, shade)
            pygame.draw.line(surface, color, (x, draw_start), (x, draw_end - 1))

            # Ceiling (dark)
            if draw_start > 0:
                pygame.draw.line(surface, (20, 20, 30), (x, 0), (x, draw_start - 1))

            # Floor
            if draw_end < screen_h:
                floor_shade = 60 if perp_dist < 3 else 40
                floor_color = (floor_shade, floor_shade, floor_shade)
                pygame.draw.line(surface, floor_color, (x, draw_end), (x, screen_h - 1))

    def render_entities(
        self, surface: "pygame.Surface", entities: list[Entity]
    ) -> None:
        """Render entities as sprites in the raycast view."""
        import pygame

        cam = self.camera
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Sort by distance (far to near)
        sprites: list[tuple[Entity, float]] = []
        for e in entities:
            if not e.active:
                continue
            dx = e.pos.x - cam.position.x
            dy = e.pos.y - cam.position.y
            dist = math.sqrt(dx * dx + dy * dy)
            sprites.append((e, dist))

        sprites.sort(key=lambda s: s[1], reverse=True)

        for entity, dist in sprites:
            dx = entity.pos.x - cam.position.x
            dy = entity.pos.y - cam.position.y

            # Transform to camera space
            transform_x = math.cos(-cam.direction) * dx - math.sin(-cam.direction) * dy
            transform_y = math.sin(-cam.direction) * dx + math.cos(-cam.direction) * dy

            if transform_y <= 0.1:
                continue

            sprite_screen_x = screen_w // 2 + int(transform_x / transform_y * screen_w / 2)
            sprite_height = int(float(screen_h) / transform_y)
            sprite_height = max(1, min(screen_h, sprite_height))

            draw_start_y = max(0, screen_h // 2 - sprite_height // 2)
            draw_end_y = min(screen_h, screen_h // 2 + sprite_height // 2)

            sprite_width = max(1, sprite_height // 2)
            draw_start_x = sprite_screen_x - sprite_width // 2
            draw_end_x = sprite_screen_x + sprite_width // 2

            # Shade by distance
            alpha = max(50, min(255, int(255 / (1 + dist * 0.1))))
            color = tuple(max(0, min(255, int(c * alpha / 255))) for c in entity.color)

            for sx in range(max(0, draw_start_x), min(screen_w, draw_end_x)):
                for sy in range(draw_start_y, draw_end_y):
                    surface.set_at((sx, sy), color)


def draw_minimap(
    surface: "pygame.Surface",
    x: int,
    y: int,
    w: int,
    h: int,
    tile_map: TileMap,
    player: Entity | None = None,
) -> None:
    """Draw a minimap overlay showing the tile map and player position."""
    import pygame

    if tile_map.width == 0 or tile_map.height == 0:
        return

    scale_x = tile_map.width / w
    scale_y = tile_map.height / h

    # Background
    pygame.draw.rect(surface, (0, 0, 0), (x - 1, y - 1, w + 2, h + 2))

    for sy in range(h):
        for sx in range(w):
            wx = int(float(sx) * scale_x)
            wy = int(float(sy) * scale_y)
            if 0 <= wx < tile_map.width and 0 <= wy < tile_map.height:
                tile = tile_map.get(wx, wy)
                color = tile.color
            else:
                color = (0, 0, 0)
            surface.set_at((x + sx, y + sy), color)

    # Player dot
    if player is not None:
        px = x + int(player.pos.x / scale_x) if scale_x > 0 else x
        py = y + int(player.pos.y / scale_y) if scale_y > 0 else y
        if x <= px < x + w and y <= py < y + h:
            pygame.draw.circle(surface, (255, 255, 0), (px, py), 2)
