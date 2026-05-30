from fastapi import APIRouter, HTTPException, Request

from app.storage.database import SessionLocal
from app.storage.db_models import RelationshipRecord

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


def _load_player_from_db(player_id: int, request: Request):
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


@router.get("/player/{player_id}")
async def get_player_relationships(request: Request, player_id: int):
    """获取玩家与所有 NPC 的好感度"""
    player_agents = getattr(request.app.state, "player_agents", {})
    player = player_agents.get(player_id)
    if not player:
        player = _load_player_from_db(player_id, request)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

    return {
        "player_id": player_id,
        "relationships": player.relationships,
    }


@router.get("/npc/{npc_id}")
async def get_npc_relationships(request: Request, npc_id: int):
    """获取 NPC 的所有关系"""
    db = SessionLocal()
    try:
        relationships = db.query(RelationshipRecord).filter(
            RelationshipRecord.subject_npc_id == npc_id
        ).all()
        return {
            "npc_id": npc_id,
            "relationships": [
                {"object_type": r.object_type, "object_id": r.object_id,
                 "affection": r.affection}
                for r in relationships
            ],
        }
    finally:
        db.close()
