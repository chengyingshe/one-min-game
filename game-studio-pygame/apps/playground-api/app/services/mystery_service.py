"""剧本杀游戏房间管理服务"""

from __future__ import annotations

import asyncio
import random
import string
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import WebSocket

from app.services.mystery_scenario import (
    CHARACTERS,
    CHARACTER_IDS,
    PRIVATE_SCRIPTS,
    PUBLIC_CLUES,
    DORM_CLUES,
    BODY_CLUES,
    TRUTH,
    PHASE_LOBBY,
    PHASE_ROLE_SELECT,
    PHASE_INTRO,
    PHASE_DISCUSS,
    PHASE_INVESTIGATE,
    PHASE_DISCUSS2,
    PHASE_VOTE,
    PHASE_REVEAL,
    MODE_SOLO,
    MODE_MULTI,
)


@dataclass
class MysteryPlayer:
    player_id: str
    display_name: str
    websocket: WebSocket | None
    char_id: str | None  # None until role assigned
    is_ai: bool = False
    joined_at: float = field(default_factory=time.time)


@dataclass
class MysteryRoom:
    room_id: str
    mode: str  # "solo" or "multi"
    phase: str = PHASE_LOBBY
    players: dict[str, MysteryPlayer] = field(default_factory=dict)
    host_id: str = ""
    max_players: int = 4
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Game state
    clues_found: set[str] = field(default_factory=set)
    public_clues_revealed: set[str] = field(default_factory=set)
    votes: dict[str, str] = field(default_factory=dict)  # player_id -> target_char_id
    dorm_votes: dict[str, str] = field(default_factory=dict)
    body_votes: dict[str, str] = field(default_factory=dict)
    dorm_searched: set[str] = field(default_factory=set)
    body_searched: set[str] = field(default_factory=set)
    chat_history: list[dict] = field(default_factory=list)
    phase_started_at: float = 0
    ai_speak_timer: float = 0


class MysteryService:
    _rooms: dict[str, MysteryRoom] = {}
    _counter: int = 0

    def generate_room_code(self) -> str:
        chars = string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789"
        return "".join(random.choices(chars, k=6))

    def create_room(
        self,
        mode: str = MODE_MULTI,
        host_name: str = "Host",
        max_players: int = 4,
    ) -> MysteryRoom:
        room_id = self.generate_room_code()
        room = MysteryRoom(
            room_id=room_id,
            mode=mode,
            players={},
            host_id="",
            max_players=max_players,
        )
        self._rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> MysteryRoom | None:
        return self._rooms.get(room_id)

    def add_player(
        self, room_id: str, player_name: str
    ) -> MysteryPlayer | None:
        room = self._rooms.get(room_id)
        if not room or room.phase != PHASE_LOBBY:
            return None
        real_count = sum(1 for p in room.players.values() if not p.is_ai)
        if real_count >= room.max_players:
            return None

        pid = f"p{self._counter}"
        self._counter += 1
        player = MysteryPlayer(pid, player_name, None)
        room.players[pid] = player
        return player

    def remove_player(self, room_id: str, player_id: str) -> None:
        room = self._rooms.get(room_id)
        if room and player_id in room.players:
            del room.players[player_id]
            if not any(not p.is_ai for p in room.players.values()):
                self.destroy_room(room_id)

    def destroy_room(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)

    def set_host(self, room_id: str, player_id: str) -> None:
        room = self._rooms.get(room_id)
        if room:
            room.host_id = player_id

    def assign_role(self, room_id: str, player_id: str, char_id: str) -> bool:
        room = self._rooms.get(room_id)
        if not room:
            return False
        player = room.players.get(player_id)
        if not player:
            return False
        # Check role not already taken
        for p in room.players.values():
            if p.char_id == char_id:
                return False
        player.char_id = char_id
        return True

    def set_phase(self, room_id: str, phase: str) -> None:
        room = self._rooms.get(room_id)
        if room:
            room.phase = phase
            room.phase_started_at = time.time()

    def auto_assign_roles(self, room_id: str) -> None:
        """Auto-assign roles. For solo: human picks first, AI gets rest. For multi: random."""
        room = self._rooms.get(room_id)
        if not room:
            return

        available = list(CHARACTER_IDS)
        random.shuffle(available)

        ai_roles = []
        human_players = [p for p in room.players.values() if not p.is_ai]

        if room.mode == MODE_SOLO and human_players:
            # In solo mode, human player picks first if they have a preference
            human = human_players[0]
            if human.char_id:
                available.remove(human.char_id)
                ai_roles = list(available)
            else:
                human.char_id = available.pop(0)
                ai_roles = list(available)
        else:
            # Multi mode: assign random roles to all human players
            for p in human_players:
                if available:
                    p.char_id = available.pop(0)
            ai_roles = list(available)

        # Create AI players for remaining roles
        for i, char_id in enumerate(ai_roles):
            char = CHARACTERS[char_id]
            ai_player = MysteryPlayer(
                f"ai_{char_id}", f"AI·{char['name']}", None,
                char_id=char_id, is_ai=True,
            )
            room.players[ai_player.player_id] = ai_player

    def add_vote(self, room_id: str, player_id: str, target_char_id: str) -> None:
        room = self._rooms.get(room_id)
        if room:
            room.votes[player_id] = target_char_id

    def get_vote_result(self, room_id: str) -> dict[str, int]:
        room = self._rooms.get(room_id)
        if not room:
            return {}
        counts: dict[str, int] = {}
        for target in room.votes.values():
            counts[target] = counts.get(target, 0) + 1
        return counts

    def check_all_voted(self, room_id: str) -> bool:
        room = self._rooms.get(room_id)
        if not room:
            return False
        human_players = [p for p in room.players.values() if not p.is_ai]
        return all(p.player_id in room.votes for p in human_players)

    def get_unassigned_roles(self, room_id: str) -> list[str]:
        room = self._rooms.get(room_id)
        if not room:
            return list(CHARACTER_IDS)
        assigned = {p.char_id for p in room.players.values() if p.char_id}
        return [c for c in CHARACTER_IDS if c not in assigned]

    def list_rooms(self) -> list[MysteryRoom]:
        return list(self._rooms.values())


mystery_service = MysteryService()
