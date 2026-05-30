"""Color constants as (R, G, B) tuples for PyGame rendering."""
from __future__ import annotations

# Text / UI colors (port of Go lipgloss styles)
TITLE_FG: tuple[int, int, int] = (250, 250, 250)
TITLE_BG: tuple[int, int, int] = (125, 86, 244)

SCORE_COLOR: tuple[int, int, int] = (255, 255, 0)

GAMEOVER_FG: tuple[int, int, int] = (255, 107, 107)
GAMEOVER_BG: tuple[int, int, int] = (51, 51, 51)

HINT_COLOR: tuple[int, int, int] = (136, 136, 136)

GRACE_COLOR: tuple[int, int, int] = (0, 255, 0)

# Difficulty tier colors
DIFFICULTY_COLORS: dict[str, tuple[int, int, int]] = {
    "easy": (0, 255, 0),
    "normal": (255, 255, 0),
    "hard": (255, 68, 68),
}

# Common game colors
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
BLUE: tuple[int, int, int] = (0, 0, 255)
YELLOW: tuple[int, int, int] = (255, 255, 0)
CYAN: tuple[int, int, int] = (0, 255, 255)
MAGENTA: tuple[int, int, int] = (255, 0, 255)
GRAY: tuple[int, int, int] = (128, 128, 128)
DARK_GRAY: tuple[int, int, int] = (64, 64, 64)
ORANGE: tuple[int, int, int] = (255, 165, 0)

# Background colors
BG_SKY: tuple[int, int, int] = (135, 206, 235)
BG_GROUND: tuple[int, int, int] = (139, 119, 101)
BG_DARK: tuple[int, int, int] = (20, 20, 30)
BG_SPACE: tuple[int, int, int] = (5, 5, 15)
