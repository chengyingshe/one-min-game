import json
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.storage.database import Base


class PlayerRecord(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    identity = Column(String(32), default="行脚商人")
    current_location = Column(String(32), default="茶馆")
    wealth = Column(Float, default=100.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NpcRecord(Base):
    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False)
    source = Column(String(64))
    occupation = Column(String(64))
    personality_json = Column(Text, default="{}")
    current_location = Column(String(32), default="茶馆")
    current_emotion = Column(String(32), default="neutral")
    speaking_style = Column(Text, default="")
    avatar_emoji = Column(String(8), default="")
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    target_location = Column(String(32), default="")
    is_moving = Column(Boolean, default=False)


class LocationRecord(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    display_name = Column(String(64))
    description = Column(Text, default="")
    type = Column(String(32), default="social")
    emoji = Column(String(8), default="")


class ItemRecord(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    type = Column(String(32), default="misc")
    base_price = Column(Float, default=10.0)
    description = Column(Text, default="")
    owner_type = Column(String(16), default="shop")
    owner_id = Column(Integer, nullable=True)


class ScheduleRecord(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    npc_id = Column(Integer, ForeignKey("npcs.id"), nullable=False)
    time_slot = Column(String(5), nullable=False)
    activity = Column(String(64))
    location = Column(String(32))


class RelationshipRecord(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_npc_id = Column(Integer, ForeignKey("npcs.id"), nullable=False)
    object_type = Column(String(16), nullable=False)
    object_id = Column(Integer, nullable=False)
    affection = Column(Float, default=50.0)


class DialogueHistoryRecord(Base):
    __tablename__ = "dialogue_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    speaker_type = Column(String(16), nullable=False)
    speaker_id = Column(Integer, nullable=False)
    listener_type = Column(String(16), nullable=False)
    listener_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    location = Column(String(32), default="")
    day_number = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TradeRecordRecord(Base):
    __tablename__ = "trade_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposer_type = Column(String(16), nullable=False)
    proposer_id = Column(Integer, nullable=False)
    receiver_npc_id = Column(Integer, ForeignKey("npcs.id"), nullable=False)
    offered_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    offered_gold = Column(Float, default=0.0)
    final_price = Column(Float, nullable=True)
    status = Column(String(16), default="proposed")
    day_number = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WorldStateRecord(Base):
    __tablename__ = "world_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), unique=True, nullable=False)
    value_json = Column(Text, default="")
