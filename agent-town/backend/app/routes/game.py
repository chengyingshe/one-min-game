from fastapi import APIRouter, HTTPException, Request

from app.models import AdvanceTimeRequest, GameStateResponse, SeedResponse

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/seed", response_model=SeedResponse)
async def seed_game(request: Request):
    from app.seed import seed_all
    db = request.app.state.db_session_factory()
    qdrant = request.app.state.qdrant
    try:
        seed_all(db, qdrant)
        return {"status": "ok", "message": "Game data initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/state", response_model=GameStateResponse)
async def get_game_state(request: Request):
    world_agent = request.app.state.world_agent
    state = await world_agent.get_world_state()

    from app.storage.database import SessionLocal
    from app.storage.db_models import NpcRecord, LocationRecord
    import json
    db = SessionLocal()
    try:
        npcs = []
        for r in db.query(NpcRecord).all():
            npcs.append({
                "id": r.id, "name": r.name, "source": r.source or "",
                "occupation": r.occupation or "",
                "personality": json.loads(r.personality_json) if r.personality_json else {},
                "current_location": r.current_location or "茶馆",
                "current_emotion": r.current_emotion or "neutral",
                "speaking_style": r.speaking_style or "",
                "avatar_emoji": r.avatar_emoji or "",
            })
        locations = [{"id": r.id, "name": r.name, "display_name": r.display_name,
                      "description": r.description, "type": r.type, "emoji": r.emoji}
                     for r in db.query(LocationRecord).all()]
        return {
            "current_day": state.get("current_day", 1),
            "current_time": state.get("current_time", "08:00"),
            "npcs": npcs,
            "locations": locations,
        }
    finally:
        db.close()


@router.post("/advance-time")
async def advance_time(request: Request, body: AdvanceTimeRequest):
    world_agent = request.app.state.world_agent
    result = await world_agent.advance_time(hours=body.hours)

    if result.get("should_consolidate_memories"):
        npc_ids = [npc.npc_id for npc in request.app.state.npc_agents]
        await world_agent.consolidate_all_memories(result["current_day"], npc_ids)

    return result
