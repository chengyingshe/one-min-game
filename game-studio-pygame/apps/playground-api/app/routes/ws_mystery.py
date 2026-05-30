"""WebSocket + REST endpoints for the murder mystery game.

WebSocket message protocol:
  Client → Server:
    {"type": "join", "name": "Player Name"}
    {"type": "start_game"}              — host only, starts role assignment + game
    {"type": "select_role", "char_id": "swordsman"}  — solo mode role selection
    {"type": "chat", "message": "..."}   — send a chat message during discuss phase
    {"type": "dorm_vote", "char_id": "hunter"}  — vote to search someone's dorm
    {"type": "body_vote", "char_id": "maid"}    — vote to search someone's body
    {"type": "accuse", "char_id": "swordsman"} — final vote for fish demon

  Server → Client:
    {"type": "lobby", "room_id": "...", "players": [...], "mode": "solo|multi"}
    {"type": "joined", "player_id": "..."}
    {"type": "phase", "phase": "discuss", "description": "..."}
    {"type": "role_assigned", "char_id": "swordsman", "name": "剑客", "script": "...", "color": [...]}
    {"type": "narration", "text": "...", "speaker": "host"}
    {"type": "chat", "player_id": "...", "char_id": "...", "char_name": "...", "message": "..."}
    {"type": "scene", "name": "mansion"}       — tells client to render a scene
    {"type": "clue", "clue": {...}}            — a clue has been revealed
    {"type": "vote_result", "votes": {...}, "result": "hunter"}  — dorm/body vote result
    {"type": "accuse_result", "votes": {...}, "winner": "swordsman", "correct": true}
    {"type": "truth", "text": "..."}
    {"type": "error", "message": "..."}
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import sys
import time
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.config import settings
from app.services.mystery_service import mystery_service, MysteryRoom
from app.services.mystery_scenario import (
    CHARACTERS,
    PUBLIC_CLUES,
    DORM_CLUES,
    BODY_CLUES,
    PHASE_LOBBY,
    PHASE_ROLE_SELECT,
    PHASE_INTRO,
    PHASE_DISCUSS,
    PHASE_INVESTIGATE,
    PHASE_DISCUSS2,
    PHASE_VOTE,
    PHASE_REVEAL,
    MODE_SOLO,
)

log = logging.getLogger("ws_mystery")
router = APIRouter(tags=["mystery"])


# ============================================================
# REST endpoints
# ============================================================


class MysteryRoomCreate(BaseModel):
    mode: str = "multi"
    host_name: str = "Host"
    max_players: int = 4


class MysteryJoin(BaseModel):
    player_name: str = "Player"


class MysteryRoleSelect(BaseModel):
    char_id: str


@router.post("/api/mystery/rooms")
def create_mystery_room(req: MysteryRoomCreate):
    room = mystery_service.create_room(
        mode=req.mode, host_name=req.host_name, max_players=req.max_players,
    )
    return {
        "room_id": room.room_id,
        "mode": room.mode,
        "max_players": room.max_players,
    }


@router.get("/api/mystery/rooms/{room_id}")
def get_mystery_room(room_id: str):
    room = mystery_service.get_room(room_id)
    if not room:
        return {"error": "Room not found"}
    return _room_response(room)


@router.post("/api/mystery/rooms/{room_id}/join")
def join_mystery_room(room_id: str, req: MysteryJoin):
    info = mystery_service.add_player(room_id, req.player_name)
    if not info:
        return {"error": "Cannot join room"}
    return {"player_id": info.player_id}


@router.get("/api/mystery/rooms")
def list_mystery_rooms():
    return [_room_response(r) for r in mystery_service.list_rooms()]


def _room_response(room: MysteryRoom) -> dict:
    players = []
    for p in room.players.values():
        players.append({
            "id": p.player_id,
            "name": p.display_name,
            "char_id": p.char_id,
            "is_ai": p.is_ai,
            "color": list(CHARACTERS[p.char_id]["color"]) if p.char_id else None,
        })
    return {
        "room_id": room.room_id,
        "mode": room.mode,
        "phase": room.phase,
        "host_id": room.host_id,
        "max_players": room.max_players,
        "players": players,
    }


# ============================================================
# Helpers
# ============================================================


async def _broadcast(room: MysteryRoom, message: dict, exclude: str | None = None):
    text = json.dumps(message, ensure_ascii=False)
    for pid, p in room.players.items():
        if pid == exclude or p.is_ai or p.websocket is None:
            continue
        try:
            await p.websocket.send_text(text)
        except Exception:
            pass


async def _send(room: MysteryRoom, player_id: str, message: dict):
    p = room.players.get(player_id)
    if p and p.websocket and not p.is_ai:
        try:
            await p.websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception:
            pass


async def _host_narrate_and_broadcast(room: MysteryRoom, context: str):
    """LLM host narration, broadcast to all players."""
    try:
        from app.services.mystery_llm import host_narrate
        text = host_narrate(context)
    except Exception:
        text = context
    await _broadcast(room, {"type": "narration", "text": text, "speaker": "host"})
    room.chat_history.append({
        "speaker": "host", "text": text, "timestamp": time.time(),
    })


async def _ai_players_speak(room: MysteryRoom):
    """Make AI players generate responses during discussion."""
    ai_players = [p for p in room.players.values() if p.is_ai and p.char_id]
    if not ai_players:
        return

    try:
        from app.services.mystery_llm import role_play_speak
        for ai in ai_players:
            response = role_play_speak(
                ai.char_id,
                room.chat_history,
                room.chat_history[-10:],
            )
            msg = {
                "type": "chat",
                "player_id": ai.player_id,
                "char_id": ai.char_id,
                "char_name": CHARACTERS[ai.char_id]["name"],
                "message": response,
                "is_ai": True,
            }
            await _broadcast(room, msg)
            room.chat_history.append({
                "speaker": ai.char_id,
                "text": response,
                "is_ai": True,
                "timestamp": time.time(),
            })
    except Exception as exc:
        log.warning("AI player error: %s", exc)


async def _ai_vote(room: MysteryRoom, vote_type: str) -> None:
    """AI players cast votes."""
    from app.services.mystery_llm import role_play_speak
    ai_players = [p for p in room.players.values() if p.is_ai and p.char_id]
    if not ai_players:
        return

    targets = list(CHARACTERS.keys())
    for ai in ai_players:
        # AI votes for a random target (not themselves if possible)
        others = [t for t in targets if t != ai.char_id]
        target = random.choice(others) if others else random.choice(targets)
        if vote_type == "dorm":
            room.dorm_votes[ai.player_id] = target
        elif vote_type == "body":
            room.body_votes[ai.player_id] = target
        elif vote_type == "accuse":
            room.votes[ai.player_id] = target


# ============================================================
# Phase transitions
# ============================================================


async def _start_game(room: MysteryRoom):
    """Start game: assign roles, enter intro phase."""
    mystery_service.auto_assign_roles(room.room_id)
    mystery_service.set_phase(room.room_id, PHASE_INTRO)

    # Send scene
    await _broadcast(room, {"type": "scene", "name": "mansion"})

    # Send role assignments
    for pid, p in room.players.items():
        if p.is_ai:
            continue
        char = CHARACTERS[p.char_id]
        try:
            from app.services.mystery_llm import role_private_script_summary
            script = role_private_script_summary(p.char_id)
        except Exception:
            script = PRIVATE_SCRIPTS[p.char_id]["secret"]
        await _send(room, pid, {
            "type": "role_assigned",
            "char_id": p.char_id,
            "name": char["name"],
            "surface_identity": char["surface_identity"],
            "script": script,
            "color": char["color"],
        })

    # Host opening narration
    await _host_narrate_and_broadcast(room, "游戏开始，请进行开场叙述")

    # After a delay, reveal public clues and move to discuss
    await asyncio.sleep(3)
    await _reveal_public_clues(room)


async def _reveal_public_clues(room: MysteryRoom):
    """Reveal all public clues and transition to discuss phase."""
    mystery_service.set_phase(room.room_id, PHASE_DISCUSS)

    for clue in PUBLIC_CLUES:
        room.public_clues_revealed.add(clue["id"])
        room.clues_found.add(clue["id"])
        await _broadcast(room, {"type": "clue", "clue": clue})
        await asyncio.sleep(1)

    await _broadcast(room, {
        "type": "phase",
        "phase": PHASE_DISCUSS,
        "description": "公开线索已展示。各位可以自由讨论、互相询问。",
    })
    await _host_narrate_and_broadcast(room, "公开线索已展示完毕，进入自由讨论阶段")


async def _start_investigate(room: MysteryRoom):
    """Transition to investigate phase."""
    mystery_service.set_phase(room.room_id, PHASE_INVESTIGATE)
    room.dorm_votes = {}
    room.body_votes = {}

    await _broadcast(room, {
        "type": "phase",
        "phase": PHASE_INVESTIGATE,
        "description": "投票搜证阶段 — 选择要搜查的宿舍和随身物品",
    })
    await _host_narrate_and_broadcast(
        room,
        "现在进入搜证阶段。请投票选择要搜查谁的宿舍和随身物品。"
        "每位玩家投票选择一个搜查目标。",
    )


async def _process_investigate_votes(room: MysteryRoom):
    """Process investigation votes and reveal clues."""
    # AI votes
    await _ai_vote(room, "dorm")
    await _ai_vote(room, "body")

    # Count dorm votes
    dorm_counts: dict[str, int] = {}
    for target in room.dorm_votes.values():
        dorm_counts[target] = dorm_counts.get(target, 0) + 1

    # Count body votes
    body_counts: dict[str, int] = {}
    for target in room.body_votes.values():
        body_counts[target] = body_counts.get(target, 0) + 1

    dorm_target = max(dorm_counts, key=dorm_counts.get) if dorm_counts else None
    body_target = max(body_counts, key=body_counts.get) if body_counts else None

    # Reveal dorm clue
    if dorm_target and dorm_target not in room.dorm_searched:
        room.dorm_searched.add(dorm_target)
        clue = DORM_CLUES[dorm_target]
        room.clues_found.add(clue["id"])
        await _broadcast(room, {"type": "scene", "name": clue["scene"]})
        await asyncio.sleep(1)
        await _broadcast(room, {"type": "clue", "clue": clue})
        try:
            from app.services.mystery_llm import host_announce_clue
            text = host_announce_clue(clue["description"])
        except Exception:
            text = f"搜查发现：{clue['description']}"
        await _broadcast(room, {"type": "narration", "text": text, "speaker": "host"})

    # Reveal body clue
    if body_target and body_target not in room.body_searched:
        room.body_searched.add(body_target)
        clue = BODY_CLUES[body_target]
        room.clues_found.add(clue["id"])
        await _broadcast(room, {"type": "scene", "name": clue["scene"]})
        await asyncio.sleep(1)
        await _broadcast(room, {"type": "clue", "clue": clue})
        try:
            from app.services.mystery_llm import host_announce_clue
            text = host_announce_clue(clue["description"])
        except Exception:
            text = f"搜查发现：{clue['description']}"
        await _broadcast(room, {"type": "narration", "text": text, "speaker": "host"})

    # Broadcast vote result
    await _broadcast(room, {
        "type": "vote_result",
        "dorm_target": dorm_target,
        "dorm_votes": dorm_counts,
        "body_target": body_target,
        "body_votes": body_counts,
    })

    # Transition to discuss2
    await asyncio.sleep(2)
    mystery_service.set_phase(room.room_id, PHASE_DISCUSS2)
    await _broadcast(room, {
        "type": "phase",
        "phase": PHASE_DISCUSS2,
        "description": "搜证完毕。根据发现的线索，继续讨论。",
    })
    await _host_narrate_and_broadcast(
        room,
        "搜证阶段结束。各位可以根据新发现的线索继续讨论，"
        "为最终投票做准备。",
    )


async def _start_vote(room: MysteryRoom):
    """Transition to vote phase."""
    mystery_service.set_phase(room.room_id, PHASE_VOTE)
    room.votes = {}

    await _broadcast(room, {
        "type": "phase",
        "phase": PHASE_VOTE,
        "description": "最终投票 — 指认你认为的鱼妖",
    })
    await _host_narrate_and_broadcast(
        room,
        "讨论结束。现在请各位投票，指认你认为的鱼妖。"
        "这是最终投票，请谨慎选择。",
    )


async def _process_final_votes(room: MysteryRoom):
    """Process final votes and reveal truth."""
    # AI votes
    await _ai_vote(room, "accuse")

    # Count votes
    counts = mystery_service.get_vote_result(room.room_id)
    winner = max(counts, key=counts.get) if counts else "swordsman"
    correct = winner == "swordsman"

    await _broadcast(room, {
        "type": "accuse_result",
        "votes": counts,
        "winner": winner,
        "winner_name": CHARACTERS[winner]["name"],
        "correct": correct,
    })

    # Reveal truth
    await asyncio.sleep(3)
    mystery_service.set_phase(room.room_id, PHASE_REVEAL)

    try:
        from app.services.mystery_llm import host_reveal_truth
        truth_text = host_reveal_truth()
    except Exception:
        truth_text = "真相揭晓：剑客 = 鱼妖（鲤鱼精）！"

    await _broadcast(room, {"type": "scene", "name": "reveal"})
    await _broadcast(room, {"type": "truth", "text": truth_text})
    await _broadcast(room, {
        "type": "phase",
        "phase": PHASE_REVEAL,
        "description": "真相已揭晓",
    })


# ============================================================
# WebSocket handler
# ============================================================


@router.websocket("/ws/mystery/{room_id}")
async def ws_mystery(websocket: WebSocket, room_id: str):
    room = mystery_service.get_room(room_id)
    if not room:
        await websocket.close(code=4040, reason="Room not found")
        return

    await websocket.accept()

    # First message must be join
    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        if msg.get("type") != "join":
            await websocket.close(code=4000, reason="Must join first")
            return
    except Exception:
        await websocket.close(code=4000, reason="Invalid join")
        return

    player_name = msg.get("name", "Player")

    # First real player becomes host
    is_first_host = len([p for p in room.players.values() if not p.is_ai]) == 0
    player_info = mystery_service.add_player(room_id, player_name)
    if not player_info:
        await websocket.close(code=4003, reason="Room full")
        return

    if is_first_host:
        mystery_service.set_host(room_id, player_info.player_id)

    player_info.websocket = websocket
    player_id = player_info.player_id

    # Send lobby update
    await _broadcast(room, {
        "type": "lobby",
        "room_id": room_id,
        "mode": room.mode,
        "host": room.host_id,
        "max_players": room.max_players,
        "players": [
            {
                "id": pid,
                "name": p.display_name,
                "char_id": p.char_id,
                "is_ai": p.is_ai,
                "color": list(CHARACTERS[p.char_id]["color"]) if p.char_id else None,
            }
            for pid, p in room.players.items()
        ],
    })

    await websocket.send_text(json.dumps({"type": "joined", "player_id": player_id}))

    # If in solo mode, show role select
    if room.mode == MODE_SOLO and room.phase == PHASE_LOBBY:
        available = mystery_service.get_unassigned_roles(room_id)
        await websocket.send_text(json.dumps({
            "type": "role_select",
            "available_roles": [
                {
                    "char_id": CHARACTERS[c]["id"],
                    "name": CHARACTERS[c]["name"],
                    "surface_identity": CHARACTERS[c]["surface_identity"],
                    "color": CHARACTERS[c]["color"],
                }
                for c in available
            ],
        }))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "start_game" and player_id == room.host_id:
                log.info("Starting mystery game in room %s", room_id)
                await _start_game(room)

            elif msg_type == "select_role" and room.mode == MODE_SOLO:
                char_id = msg.get("char_id", "")
                if char_id in CHARACTER_IDS:
                    player_info.char_id = char_id
                    await _send(room, player_id, {
                        "type": "role_selected",
                        "char_id": char_id,
                        "name": CHARACTERS[char_id]["name"],
                    })

            elif msg_type == "chat" and room.phase in (PHASE_DISCUSS, PHASE_DISCUSS2):
                message_text = msg.get("message", "").strip()
                if not message_text:
                    continue

                chat_msg = {
                    "type": "chat",
                    "player_id": player_id,
                    "char_id": player_info.char_id,
                    "char_name": CHARACTERS[player_info.char_id]["name"] if player_info.char_id else player_name,
                    "message": message_text,
                    "color": CHARACTERS[player_info.char_id]["color"] if player_info.char_id else [200, 200, 200],
                }
                await _broadcast(room, chat_msg)
                room.chat_history.append({
                    "speaker": player_info.char_id,
                    "text": message_text,
                    "is_ai": False,
                    "timestamp": time.time(),
                })

                # Trigger AI responses
                asyncio.create_task(_ai_delayed_speak(room))

            elif msg_type == "end_discuss" and player_id == room.host_id:
                if room.phase == PHASE_DISCUSS:
                    await _start_investigate(room)
                elif room.phase == PHASE_DISCUSS2:
                    await _start_vote(room)

            elif msg_type == "dorm_vote" and room.phase == PHASE_INVESTIGATE:
                target = msg.get("char_id", "")
                if target in CHARACTER_IDS:
                    room.dorm_votes[player_id] = target
                    # Check if all human players voted
                    human = [p for p in room.players.values() if not p.is_ai]
                    if len(room.dorm_votes) >= len(human):
                        await _process_investigate_votes(room)

            elif msg_type == "body_vote" and room.phase == PHASE_INVESTIGATE:
                target = msg.get("char_id", "")
                if target in CHARACTER_IDS:
                    room.body_votes[player_id] = target
                    human = [p for p in room.players.values() if not p.is_ai]
                    if len(room.body_votes) >= len(human):
                        await _process_investigate_votes(room)

            elif msg_type == "accuse" and room.phase == PHASE_VOTE:
                target = msg.get("char_id", "")
                if target in CHARACTER_IDS:
                    mystery_service.add_vote(room_id, player_id, target)
                    human = [p for p in room.players.values() if not p.is_ai]
                    if mystery_service.check_all_voted(room_id):
                        await _process_final_votes(room)

    except WebSocketDisconnect:
        log.info("Player %s disconnected from mystery room %s", player_id, room_id)
    except Exception as exc:
        log.exception("Error for player %s in mystery room %s: %s", player_id, room_id, exc)
    finally:
        player_info.websocket = None
        mystery_service.remove_player(room_id, player_id)


async def _ai_delayed_speak(room: MysteryRoom):
    """AI players respond after a short delay."""
    await asyncio.sleep(2 + len(room.players) * 0.5)
    if room.phase not in (PHASE_DISCUSS, PHASE_DISCUSS2):
        return
    await _ai_players_speak(room)
