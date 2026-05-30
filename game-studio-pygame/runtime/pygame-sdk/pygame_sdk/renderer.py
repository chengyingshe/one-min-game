"""PyGame renderer with real display and headless (Docker) modes."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pygame

from .styles import (
    BG_DARK,
    GAMEOVER_BG,
    GAMEOVER_FG,
    GRACE_COLOR,
    HINT_COLOR,
    SCORE_COLOR,
    TITLE_BG,
    TITLE_FG,
    WHITE,
)

if TYPE_CHECKING:
    from .entity import Entity


class Renderer:
    """PyGame-based renderer with init/init_headless modes.

    Provides draw_entity, draw_text, and capture_screenshot.
    """

    def __init__(self, width: int = 800, height: int = 600, fps: int = 60) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self._initialized = False
        self._headless = False
        self._font: pygame.font.Font | None = None
        self._font_large: pygame.font.Font | None = None
        self._font_small: pygame.font.Font | None = None

    def init(self) -> None:
        """Initialize pygame with a real display window."""
        pygame.init()
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("One-Min Game")
        self.clock = pygame.time.Clock()
        self._init_fonts()
        self._initialized = True
        self._headless = False

    def init_headless(self) -> None:
        """Initialize pygame in headless mode for Docker / CI."""
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self._init_fonts()
        self._initialized = True
        self._headless = True

    def _init_fonts(self) -> None:
        """Load default system fonts."""
        try:
            self._font = pygame.font.SysFont("monospace", 20)
            self._font_large = pygame.font.SysFont("monospace", 36)
            self._font_small = pygame.font.SysFont("monospace", 14)
        except Exception:
            self._font = pygame.font.Font(None, 20)
            self._font_large = pygame.font.Font(None, 36)
            self._font_small = pygame.font.Font(None, 14)

    def quit(self) -> None:
        """Shut down pygame."""
        if self._initialized:
            pygame.quit()
            self._initialized = False

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def clear(self, color: tuple[int, int, int] = BG_DARK) -> None:
        """Fill the screen with a background color."""
        if self.screen is not None:
            self.screen.fill(color)

    def draw_entity(self, entity: Entity) -> None:
        """Draw an entity as a colored rectangle with optional symbol overlay."""
        if self.screen is None or not entity.active:
            return

        rect = pygame.Rect(
            int(entity.pos.x),
            int(entity.pos.y),
            int(entity.size.x),
            int(entity.size.y),
        )
        pygame.draw.rect(self.screen, entity.color, rect)

        # Draw symbol text on top if font available
        if self._font_small and entity.symbol:
            text_surf = self._font_small.render(entity.symbol, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def draw_entities(self, entities: list[Entity]) -> None:
        """Draw all active entities."""
        for e in entities:
            if e.active:
                self.draw_entity(e)

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int] = WHITE,
        font: str = "normal",
    ) -> None:
        """Draw text at pixel position.

        font: 'normal', 'large', or 'small'
        """
        if self.screen is None:
            return

        f = self._font
        if font == "large" and self._font_large:
            f = self._font_large
        elif font == "small" and self._font_small:
            f = self._font_small

        if f is None:
            return

        text_surf = f.render(text, True, color)
        self.screen.blit(text_surf, (x, y))

    def draw_text_centered(
        self,
        text: str,
        y: int,
        color: tuple[int, int, int] = WHITE,
        font: str = "normal",
    ) -> None:
        """Draw text horizontally centered at given y."""
        if self.screen is None:
            return

        f = self._font
        if font == "large" and self._font_large:
            f = self._font_large
        elif font == "small" and self._font_small:
            f = self._font_small

        if f is None:
            return

        text_surf = f.render(text, True, color)
        text_rect = text_surf.get_rect(centerx=self.width // 2, y=y)
        self.screen.blit(text_surf, text_rect)

    def draw_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: tuple[int, int, int],
        filled: bool = True,
    ) -> None:
        """Draw a rectangle (filled or outline)."""
        if self.screen is None:
            return
        rect = pygame.Rect(x, y, w, h)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 1)

    def draw_title(self, text: str) -> None:
        """Draw styled title text centered on screen."""
        self.draw_text_centered(text, self.height // 3, TITLE_FG, font="large")

    def draw_score(self, score: int) -> None:
        """Draw score in top-right corner."""
        self.draw_text(f"Score: {score}", self.width - 150, 10, SCORE_COLOR)

    def draw_game_over(self, score: int, best: int) -> None:
        """Draw game over overlay."""
        # Semi-transparent overlay
        if self.screen is not None:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

        self.draw_text_centered("GAME OVER", self.height // 3, GAMEOVER_FG, font="large")
        self.draw_text_centered(f"Score: {score}", self.height // 2, WHITE)
        self.draw_text_centered(f"Best: {best}", self.height // 2 + 30, SCORE_COLOR)
        self.draw_text_centered("Press R to restart", self.height // 2 + 80, HINT_COLOR, font="small")

    def draw_grace_indicator(self, remaining_frames: int) -> None:
        """Draw grace period indicator."""
        seconds = remaining_frames // 60 + 1
        self.draw_text_centered(f"Grace Period: {seconds}s", 10, GRACE_COLOR, font="small")

    def draw_hint(self, text: str) -> None:
        """Draw hint text centered near bottom."""
        self.draw_text_centered(text, self.height - 40, HINT_COLOR, font="small")

    def present(self) -> None:
        """Flip display and tick the clock."""
        if self.screen is not None and not self._headless:
            pygame.display.flip()
        if self.clock is not None:
            self.clock.tick(self.fps)

    def capture_screenshot(self) -> bytes:
        """Capture current screen as PNG bytes."""
        from .screenshot import capture_screenshot

        if self.screen is None:
            return b""
        return capture_screenshot(self.screen)

    def too_small(self, min_width: int, min_height: int) -> str:
        """Return an error string if screen is too small."""
        if self.width < min_width or self.height < min_height:
            return (
                f"Screen too small! Need at least {min_width}x{min_height}, "
                f"got {self.width}x{self.height}"
            )
        return ""
