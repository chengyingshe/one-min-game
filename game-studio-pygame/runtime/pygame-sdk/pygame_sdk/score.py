"""Score tracking with best-score persistence."""
from __future__ import annotations


class ScoreManager:
    """Track current and best score for a game session."""

    def __init__(self) -> None:
        self.current: int = 0
        self.best: int = 0

    def add(self, points: int) -> None:
        self.current += points

    def reset(self) -> None:
        self.current = 0

    def update_best(self) -> bool:
        """Update best if current exceeds it. Returns True if new best."""
        if self.current > self.best:
            self.best = self.current
            return True
        return False
