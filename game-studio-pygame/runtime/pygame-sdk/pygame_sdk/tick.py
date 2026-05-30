"""Tick scheduling for frame-based game timing."""
from __future__ import annotations


class TickScheduler:
    """Frame-counting scheduler for periodic events.

    Uses frame counting instead of Go's tea.Tick for pygame integration.
    """

    def __init__(self, fps: int = 60) -> None:
        self.fps: int = fps
        self.frame: int = 0

    def advance(self) -> int:
        """Advance one frame. Returns new frame number."""
        self.frame += 1
        return self.frame

    def should_spawn(self, every: int) -> bool:
        """Return True every N frames."""
        return self.frame % every == 0

    def elapsed_seconds(self) -> float:
        """Seconds elapsed since start (approximate, based on frame count)."""
        return self.frame / self.fps if self.fps > 0 else 0.0

    def reset(self) -> None:
        self.frame = 0
