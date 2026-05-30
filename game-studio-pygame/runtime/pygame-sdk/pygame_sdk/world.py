"""Tile-based world map for roguelike and dungeon games."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TileType:
    """Describes a single tile type."""

    symbol: str = " "
    walkable: bool = True
    solid: bool = False
    color: tuple[int, int, int] = (128, 128, 128)


class TileMap:
    """Grid-based tile map with lookup and rendering."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # Fill with empty walkable tiles
        self.tiles: list[list[TileType]] = [
            [TileType() for _ in range(width)] for _ in range(height)
        ]

    def set(
        self,
        x: int,
        y: int,
        symbol: str = " ",
        walkable: bool = True,
        solid: bool = False,
        color: tuple[int, int, int] = (128, 128, 128),
    ) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = TileType(
                symbol=symbol, walkable=walkable, solid=solid, color=color
            )

    def get(self, x: int, y: int) -> TileType:
        """Get tile at position. Returns wall tile for out-of-bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType(symbol="#", walkable=False, solid=True, color=(100, 100, 100))

    def is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.tiles[y][x].walkable

    def is_solid(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.tiles[y][x].solid

    def load_from_strings(
        self,
        grid: list[str],
        legend: dict[str, TileType],
    ) -> None:
        """Load tile map from a list of strings and a symbol->TileType legend."""
        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if x >= self.width or y >= self.height:
                    continue
                if ch in legend:
                    self.tiles[y][x] = TileType(
                        symbol=legend[ch].symbol,
                        walkable=legend[ch].walkable,
                        solid=legend[ch].solid,
                        color=legend[ch].color,
                    )
                else:
                    self.tiles[y][x] = TileType(
                        symbol=ch, walkable=False, solid=True, color=(100, 100, 100)
                    )

    def render_region(
        self,
        surface: "pygame.Surface",
        tile_size: int,
        offset_x: int = 0,
        offset_y: int = 0,
        view_w: int | None = None,
        view_h: int | None = None,
    ) -> None:
        """Render a region of the tile map onto a pygame surface.

        Each tile is drawn as a tile_size x tile_size colored rectangle
        with the tile symbol overlaid as text.
        """
        import pygame

        if surface is None:
            return

        if view_w is None:
            view_w = surface.get_width() // tile_size
        if view_h is None:
            view_h = surface.get_height() // tile_size

        font = pygame.font.Font(None, tile_size)

        for sy in range(view_h):
            for sx in range(view_w):
                wx = sx + offset_x
                wy = sy + offset_y
                px = sx * tile_size
                py = sy * tile_size

                if 0 <= wx < self.width and 0 <= wy < self.height:
                    tile = self.tiles[wy][wx]
                else:
                    tile = TileType(symbol=" ", walkable=False, solid=False, color=(0, 0, 0))

                pygame.draw.rect(surface, tile.color, (px, py, tile_size, tile_size))
                if tile.symbol.strip():
                    text_surf = font.render(tile.symbol, True, (255, 255, 255))
                    text_rect = text_surf.get_rect(
                        center=(px + tile_size // 2, py + tile_size // 2)
                    )
                    surface.blit(text_surf, text_rect)

    def to_string_grid(self) -> list[str]:
        """Export tile map as list of strings (for pathfinding, etc)."""
        rows: list[str] = []
        for y in range(self.height):
            row = "".join(self.tiles[y][x].symbol for x in range(self.width))
            rows.append(row)
        return rows
