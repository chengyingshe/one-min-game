"""REST API for multiplayer rooms."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.room_service import room_service

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


class RoomCreateRequest(BaseModel):
    game_name: str
    host_name: str = "Player 1"
    max_players: int = 4


class JoinRequest(BaseModel):
    player_name: str = "Player"


@router.post("")
def create_room(req: RoomCreateRequest):
    room = room_service.create_room(req.game_name, req.host_name, req.max_players)
    return _room_response(room)


@router.get("/{room_id}")
def get_room(room_id: str):
    room = room_service.get_room(room_id)
    if not room:
        return {"error": "Room not found"}
    return _room_response(room)


@router.post("/{room_id}/join")
def join_room(room_id: str, req: JoinRequest):
    info = room_service.add_player(room_id, req.player_name)
    if not info:
        return {"error": "Cannot join room"}
    return {
        "player_id": info.player_id,
        "color": list(info.color),
    }


@router.get("")
def list_rooms():
    return [_room_response(r) for r in room_service.list_rooms()]


def _room_response(room):
    return {
        "room_id": room.room_id,
        "game_name": room.game_name,
        "host_id": room.host_id,
        "status": room.status,
        "max_players": room.max_players,
        "players": [
            {"id": pid, "name": p.display_name, "color": list(p.color)}
            for pid, p in room.players.items()
        ],
    }
