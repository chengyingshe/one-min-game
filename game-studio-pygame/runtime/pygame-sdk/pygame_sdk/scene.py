"""Scene state machine for game flow (menu, gameplay, paused, game over)."""
from __future__ import annotations

from enum import IntEnum


class SceneState(IntEnum):
    MENU = 0
    GAMEPLAY = 1
    PAUSED = 2
    GAME_OVER = 3


class SceneManager:
    """Manages scene transitions with previous-state tracking."""

    def __init__(self) -> None:
        self.current: SceneState = SceneState.MENU
        self.previous: SceneState = SceneState.MENU

    def transition(self, to: SceneState) -> None:
        """Switch to a new scene state, remembering the previous one."""
        self.previous = self.current
        self.current = to

    def is_state(self, state: SceneState) -> bool:
        return self.current == state

    def is_playing(self) -> bool:
        return self.current == SceneState.GAMEPLAY

    def toggle_pause(self) -> None:
        """Toggle between gameplay and paused states."""
        if self.current == SceneState.GAMEPLAY:
            self.transition(SceneState.PAUSED)
        elif self.current == SceneState.PAUSED:
            self.transition(SceneState.GAMEPLAY)
