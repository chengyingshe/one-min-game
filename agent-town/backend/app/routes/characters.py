from fastapi import APIRouter, HTTPException, Request

from app.models import NpcResponse, PlayerCreate, PlayerResponse

router = APIRouter(prefix="/api", tags=["characters"])


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


@router.post("/player", response_model=PlayerResponse)
async def create_player(request: Request, body: PlayerCreate):
    from app.storage.database import SessionLocal
    from app.storage.db_models import PlayerRecord
    from app.agents.player_agent import PlayerAgent

    db = SessionLocal()
    try:
        record = PlayerRecord(name=body.name, identity=body.identity)
        db.add(record)
        db.commit()
        db.refresh(record)

        agent = PlayerAgent(
            player_id=record.id,
            player_data={"name": record.name, "identity": record.identity,
                         "current_location": record.current_location, "wealth": record.wealth},
        )
        # Store player agent in app state keyed by id
        if not hasattr(request.app.state, "player_agents"):
            request.app.state.player_agents = {}
        request.app.state.player_agents[record.id] = agent

        return agent.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/player/{player_id}", response_model=PlayerResponse)
async def get_player(request: Request, player_id: int):
    agents = getattr(request.app.state, "player_agents", {})
    agent = agents.get(player_id)
    if not agent:
        agent = _load_player_from_db(player_id, request)
        if not agent:
            raise HTTPException(status_code=404, detail="Player not found")
    return agent.to_dict()


@router.get("/npcs", response_model=list[NpcResponse])
async def list_npcs(request: Request):
    from app.storage.database import SessionLocal
    from app.storage.db_models import NpcRecord
    import json

    db = SessionLocal()
    try:
        result = []
        for r in db.query(NpcRecord).all():
            result.append({
                "id": r.id, "name": r.name, "source": r.source or "",
                "occupation": r.occupation or "",
                "personality": json.loads(r.personality_json) if r.personality_json else {},
                "current_location": r.current_location or "茶馆",
                "current_emotion": r.current_emotion or "neutral",
                "speaking_style": r.speaking_style or "",
                "avatar_emoji": r.avatar_emoji or "",
            })
        return result
    finally:
        db.close()


@router.get("/npcs/{npc_id}", response_model=NpcResponse)
async def get_npc(request: Request, npc_id: int):
    from app.storage.database import SessionLocal
    from app.storage.db_models import NpcRecord
    import json

    db = SessionLocal()
    try:
        r = db.query(NpcRecord).filter(NpcRecord.id == npc_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="NPC not found")
        return {
            "id": r.id, "name": r.name, "source": r.source or "",
            "occupation": r.occupation or "",
            "personality": json.loads(r.personality_json) if r.personality_json else {},
            "current_location": r.current_location or "茶馆",
            "current_emotion": r.current_emotion or "neutral",
            "speaking_style": r.speaking_style or "",
            "avatar_emoji": r.avatar_emoji or "",
        }
    finally:
        db.close()
