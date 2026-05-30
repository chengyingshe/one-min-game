"""Input mapping from pygame key constants to game actions."""
from __future__ import annotations

from enum import IntEnum

import pygame


class InputAction(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    PRIMARY = 4
    SECONDARY = 5
    PAUSE = 6
    QUIT = 7
    RESTART = 8


class InputMapper:
    """Maps pygame key constants to InputActions."""

    def __init__(self) -> None:
        self._bindings: dict[int, InputAction] = {}

    @classmethod
    def default(cls) -> InputMapper:
        """Create a mapper with standard key bindings."""
        m = cls()
        m.map(pygame.K_UP, InputAction.UP)
        m.map(pygame.K_w, InputAction.UP)
        m.map(pygame.K_DOWN, InputAction.DOWN)
        m.map(pygame.K_s, InputAction.DOWN)
        m.map(pygame.K_LEFT, InputAction.LEFT)
        m.map(pygame.K_a, InputAction.LEFT)
        m.map(pygame.K_RIGHT, InputAction.RIGHT)
        m.map(pygame.K_d, InputAction.RIGHT)
        m.map(pygame.K_SPACE, InputAction.PRIMARY)
        m.map(pygame.K_RETURN, InputAction.PRIMARY)
        m.map(pygame.K_LSHIFT, InputAction.SECONDARY)
        m.map(pygame.K_p, InputAction.PAUSE)
        m.map(pygame.K_ESCAPE, InputAction.QUIT)
        m.map(pygame.K_q, InputAction.QUIT)
        m.map(pygame.K_r, InputAction.RESTART)
        return m

    def map(self, key: int, action: InputAction) -> None:
        self._bindings[key] = action

    def action(self, key: int) -> tuple[InputAction | None, bool]:
        """Look up action for a key. Returns (action, found)."""
        a = self._bindings.get(key)
        return a, a is not None

    def has_action(self, key: int) -> bool:
        return key in self._bindings

    def process_events(self) -> list[InputAction]:
        """Process all pygame events and return list of triggered actions.

        Also returns pygame.QUIT as InputAction.QUIT.
        """
        actions: list[InputAction] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append(InputAction.QUIT)
            elif event.type == pygame.KEYDOWN:
                a, found = self.action(event.key)
                if found and a is not None:
                    actions.append(a)
        return actions

    def poll_pressed(self) -> list[InputAction]:
        """Return actions for all currently-held keys."""
        keys = pygame.key.get_pressed()
        actions: list[InputAction] = []
        for key_code, action in self._bindings.items():
            if keys[key_code]:
                actions.append(action)
        return actions
