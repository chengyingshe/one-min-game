"""Multiplayer support for PyGame SDK games.

Provides per-player input tracking and player slot management for games
that support multiple players via the game_stream_runner subprocess protocol.
"""
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entity import Entity

# Key name → pygame key constant mapping (mirrors game_stream_runner.KEY_MAP)
_KEY_MAP: dict[str, int] = {}


def _ensure_key_map():
    global _KEY_MAP
    if _KEY_MAP:
        return
    import pygame
    _KEY_MAP.update({
        "up": pygame.K_UP, "down": pygame.K_DOWN,
        "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
        "space": pygame.K_SPACE, "enter": pygame.K_RETURN,
        "escape": pygame.K_ESCAPE, "w": pygame.K_w, "a": pygame.K_a,
        "s": pygame.K_s, "d": pygame.K_d, "z": pygame.K_z,
        "x": pygame.K_x, "c": pygame.K_c, "q": pygame.K_q,
        "e": pygame.K_e, "r": pygame.K_r, "shift": pygame.K_LSHIFT,
        "ctrl": pygame.K_LCTRL, "tab": pygame.K_TAB,
        "backspace": pygame.K_BACKSPACE, "b": pygame.K_b, "f": pygame.K_f,
    })


class PlayerSlot:
    """Represents one player in a multiplayer game."""

    __slots__ = (
        "player_id", "display_name", "color", "entity",
        "connected", "_key_state",
    )

    def __init__(
        self,
        player_id: str,
        display_name: str = "",
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self.player_id: str = player_id
        self.display_name: str = display_name
        self.color: tuple[int, int, int] = color
        self.entity: Entity | None = None
        self.connected: bool = True
        self._key_state: dict[int, int] = defaultdict(int)

    def is_key_down(self, pygame_key: int) -> bool:
        return bool(self._key_state.get(pygame_key, 0))

    def get_keys_pressed(self) -> dict[int, int]:
        return dict(self._key_state)


class MultiplayerManager:
    """Manages multiple players in a multiplayer game.

    Games use this instead of pygame.key.get_pressed() for per-player input.
    The game_stream_runner calls handle_network_message() to feed tagged input.
    """

    def __init__(self, max_players: int = 4) -> None:
        self._players: dict[str, PlayerSlot] = {}
        self.max_players: int = max_players
        self._started: bool = False

    def add_player(
        self,
        player_id: str,
        display_name: str = "",
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> PlayerSlot:
        slot = PlayerSlot(player_id, display_name, color)
        self._players[player_id] = slot
        return slot

    def remove_player(self, player_id: str) -> None:
        if player_id in self._players:
            self._players[player_id].connected = False

    def get_player(self, player_id: str) -> PlayerSlot | None:
        return self._players.get(player_id)

    def get_all_players(self) -> list[PlayerSlot]:
        return list(self._players.values())

    def get_connected_players(self) -> list[PlayerSlot]:
        return [p for p in self._players.values() if p.connected]

    def player_count(self) -> int:
        return len(self._players)

    def connected_count(self) -> int:
        return sum(1 for p in self._players.values() if p.connected)

    def update_key_state(
        self, player_id: str, pygame_key: int, pressed: bool
    ) -> None:
        slot = self._players.get(player_id)
        if slot:
            slot._key_state[pygame_key] = 1 if pressed else 0

    def handle_network_message(self, msg: dict) -> None:
        _ensure_key_map()
        msg_type = msg.get("type", "")

        if msg_type == "start_game":
            self._started = True
            for p in msg.get("players", []):
                pid = p.get("id", "")
                name = p.get("name", "")
                color_raw = p.get("color", [255, 255, 255])
                color = tuple(color_raw[:3]) if len(color_raw) >= 3 else (255, 255, 255)
                self.add_player(pid, name, color)

        elif msg_type in ("keydown", "keyup") and "player" in msg:
            pid = msg["player"]
            key_name = msg.get("key", "")
            pygame_key = _KEY_MAP.get(key_name)
            if pygame_key is not None:
                self.update_key_state(pid, pygame_key, msg_type == "keydown")

        elif msg_type == "player_left":
            pid = msg.get("player_id", "")
            if pid:
                self.remove_player(pid)

    def is_started(self) -> bool:
        return self._started
