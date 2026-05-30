from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# --- Player ---
class PlayerCreate(BaseModel):
    name: str
    identity: str = "行脚商人"

class PlayerResponse(BaseModel):
    id: int
    name: str
    identity: str
    current_location: str
    wealth: float
    inventory: list[dict] = []
    relationships: dict[int, float] = {}


# --- NPC ---
class NpcResponse(BaseModel):
    id: int
    name: str
    source: str
    occupation: str
    personality: dict = {}
    current_location: str
    current_emotion: str
    speaking_style: str = ""
    avatar_emoji: str = ""


# --- Dialogue ---
class DialogueRequest(BaseModel):
    player_id: int
    npc_id: int
    content: str
    location: str = "茶馆"

class DialogueResponse(BaseModel):
    npc_id: int
    npc_name: str
    reply: str
    emotion: str = "neutral"
    location: str = "茶馆"
    affection_delta: float = 0.0
    memories_used: int = 0


# --- Trade ---
class TradeProposeRequest(BaseModel):
    player_id: int
    npc_id: int
    offered_item_name: str = ""
    offered_gold: float = 0.0
    npc_item_name: str
    npc_item_price: float = 0.0

class TradeResponse(BaseModel):
    status: str
    decision: str  # accept / counter / reject
    npc_reply: str
    fair_price: float
    counter_offer: Optional[float] = None


# --- Memory ---
class MemoryItem(BaseModel):
    id: str
    event: str
    emotion: str = "neutral"
    importance: float = 0.0
    tier: str = "short_term"
    similarity: Optional[float] = None


# --- Game State ---
class GameStateResponse(BaseModel):
    current_day: int
    current_time: str
    npcs: list[NpcResponse]
    locations: list[dict]


class AdvanceTimeRequest(BaseModel):
    hours: int = 1


class SeedResponse(BaseModel):
    status: str
    message: str
