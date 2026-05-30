from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models import DialogueRequest, DialogueResponse
from app.storage.database import get_db
from app.storage.db_models import DialogueHistoryRecord, RelationshipRecord

router = APIRouter(prefix="/api/dialogue", tags=["dialogue"])


def _load_player_from_db(player_id: int, request: Request):
    """Load player from DB and create PlayerAgent if not in memory."""
    from app.storage.database import SessionLocal
    from app.storage.db_models import PlayerRecord
    from app.agents.player_agent import PlayerAgent

    db = SessionLocal()
    try:
        record = db.query(PlayerRecord).filter(PlayerRecord.id == player_id).first()
        if not record:
            return None
        agent = PlayerAgent(
            player_id=record.id,
            player_data={
                "name": record.name, "identity": record.identity,
                "current_location": record.current_location, "wealth": record.wealth,
            },
        )
        request.app.state.player_agents[record.id] = agent
        return agent
    finally:
        db.close()


@router.post("", response_model=DialogueResponse)
async def send_dialogue(request: Request, body: DialogueRequest):
    npc_agents = getattr(request.app.state, "npc_agents", [])
    player_agents = getattr(request.app.state, "player_agents", {})
    world_agent = request.app.state.world_agent

    npc = next((a for a in npc_agents if a.npc_id == body.npc_id), None)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    player = player_agents.get(body.player_id)
    if not player:
        player = _load_player_from_db(body.player_id, request)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

    # Get current world state for day number
    ws = await world_agent.get_world_state()
    day_number = ws.get("current_day", 1)

    from app.core.message import Message, Role
    from app.storage.database import SessionLocal

    affection = player.get_affection(body.npc_id)

    input_msg = Message(
        role=Role.USER, content=body.content,
        metadata={"location": body.location, "affection": affection, "day_number": day_number},
    )
    reply = await npc.run(input_msg)

    # Update affection
    delta = reply.metadata.get("affection_delta", 0)
    player.update_affection(body.npc_id, delta)

    # Persist dialogue + relationship
    db = SessionLocal()
    try:
        db.add(DialogueHistoryRecord(
            speaker_type="player", speaker_id=body.player_id,
            listener_type="npc", listener_id=body.npc_id,
            content=body.content, location=body.location, day_number=day_number,
        ))
        db.add(DialogueHistoryRecord(
            speaker_type="npc", speaker_id=body.npc_id,
            listener_type="player", listener_id=body.player_id,
            content=reply.content, location=body.location, day_number=day_number,
        ))
        # Upsert relationship
        rel = db.query(RelationshipRecord).filter(
            RelationshipRecord.subject_npc_id == body.npc_id,
            RelationshipRecord.object_type == "player",
            RelationshipRecord.object_id == body.player_id,
        ).first()
        if rel:
            rel.affection = max(0, min(100, rel.affection + delta))
        else:
            db.add(RelationshipRecord(
                subject_npc_id=body.npc_id, object_type="player",
                object_id=body.player_id, affection=50.0 + delta,
            ))
        db.commit()
    finally:
        db.close()

    return DialogueResponse(
        npc_id=body.npc_id, npc_name=npc.name,
        reply=reply.content, emotion=reply.metadata.get("emotion", "neutral"),
        location=body.location, affection_delta=delta,
        memories_used=reply.metadata.get("memories_used", 0),
    )


@router.get("/history/{npc_id}")
async def get_dialogue_history(request: Request, npc_id: int, player_id: int = 1, limit: int = 50):
    from app.storage.database import SessionLocal
    db = SessionLocal()
    try:
        records = (
            db.query(DialogueHistoryRecord)
            .filter(
                ((DialogueHistoryRecord.speaker_id == player_id) & (DialogueHistoryRecord.listener_id == npc_id))
                | ((DialogueHistoryRecord.speaker_id == npc_id) & (DialogueHistoryRecord.listener_id == player_id))
            )
            .order_by(DialogueHistoryRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "history": [
                {"speaker_type": r.speaker_type, "speaker_id": r.speaker_id,
                 "content": r.content, "location": r.location, "day_number": r.day_number,
                 "created_at": r.created_at.isoformat()}
                for r in reversed(records)
            ]
        }
    finally:
        db.close()


@router.get("/npc-logs")
async def get_npc_dialogue_logs(request: Request, limit: int = 50):
    """获取 NPC 之间的对话历史"""
    from app.storage.database import SessionLocal
    db = SessionLocal()
    try:
        records = (
            db.query(DialogueHistoryRecord)
            .filter(
                (DialogueHistoryRecord.speaker_type == "npc")
                & (DialogueHistoryRecord.listener_type == "npc")
            )
            .order_by(DialogueHistoryRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "logs": [
                {"speaker_type": r.speaker_type, "speaker_id": r.speaker_id,
                 "listener_type": r.listener_type, "listener_id": r.listener_id,
                 "content": r.content, "location": r.location, "day_number": r.day_number,
                 "created_at": r.created_at.isoformat()}
                for r in reversed(records)
            ]
        }
    finally:
        db.close()
