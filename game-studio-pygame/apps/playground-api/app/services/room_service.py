"""In-memory room manager for multiplayer game sessions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import WebSocket


@dataclass
class PlayerInfo:
    player_id: str
    display_name: str
    websocket: WebSocket | None
    color: tuple[int, int, int]


@dataclass
class GameRoom:
    room_id: str
    game_name: str
    host_id: str
    players: dict[str, PlayerInfo]
    process: object | None  # asyncio.subprocess.Process
    status: str  # "waiting" | "starting" | "running" | "finished"
    created_at: datetime
    max_players: int = 4


class RoomService:
    _rooms: dict[str, GameRoom] = {}
    _counter: int = 0
    _PLAYER_COLORS = [
        (255, 220, 50), (80, 160, 255), (80, 220, 80), (220, 80, 80),
    ]

    def generate_room_code(self) -> str:
        import random, string
        return "".join(random.choices(string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789", k=6))

    def create_room(self, game_name: str, host_name: str = "", max_players: int = 4) -> GameRoom:
        room_id = self.generate_room_code()
        room = GameRoom(
            room_id=room_id,
            game_name=game_name,
            host_id="",
            players={},
            process=None,
            status="waiting",
            created_at=datetime.now(timezone.utc),
            max_players=max_players,
        )
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> GameRoom | None:
        return self._rooms.get(room_id)

    def add_player(self, room_id: str, player_name: str) -> PlayerInfo | None:
        room = self._rooms.get(room_id)
        if not room or room.status != "waiting":
            return None
        connected = sum(1 for _ in room.players.values())
        if connected >= room.max_players:
            return None
        idx = len(room.players)
        pid = f"p{idx + 1}"
        color = self._PLAYER_COLORS[idx % len(self._PLAYER_COLORS)]
        info = PlayerInfo(pid, player_name, None, color)
        room.players[pid] = info
        return info

    def remove_player(self, room_id: str, player_id: str) -> None:
        room = self._rooms.get(room_id)
        if room and player_id in room.players:
            del room.players[player_id]
            if not room.players:
                self.destroy_room(room_id)

    def destroy_room(self, room_id: str) -> None:
        room = self._rooms.pop(room_id, None)
        if room and room.process:
            try:
                room.process.terminate()
            except Exception:
                pass

    def list_rooms(self) -> list[GameRoom]:
        return list(self._rooms.values())


room_service = RoomService()
