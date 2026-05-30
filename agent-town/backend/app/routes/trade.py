from fastapi import APIRouter, HTTPException, Request

from app.models import TradeProposeRequest, TradeResponse
from app.storage.db_models import ItemRecord, TradeRecordRecord

router = APIRouter(prefix="/api/trade", tags=["trade"])


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


@router.post("/propose", response_model=TradeResponse)
async def propose_trade(request: Request, body: TradeProposeRequest):
    npc_agents = getattr(request.app.state, "npc_agents", [])
    player_agents = getattr(request.app.state, "player_agents", {})

    npc = next((a for a in npc_agents if a.npc_id == body.npc_id), None)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    player = player_agents.get(body.player_id)
    if not player:
        player = _load_player_from_db(body.player_id, request)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

    affection = player.get_affection(body.npc_id)
    result = await npc.evaluate_trade({
        "affection": affection,
        "offered_item_name": body.offered_item_name,
        "offered_gold": body.offered_gold,
        "npc_item_name": body.npc_item_name,
        "npc_item_price": body.npc_item_price,
    })

    # Persist trade record
    from app.storage.database import SessionLocal
    from app.storage.db_models import RelationshipRecord
    db = SessionLocal()
    try:
        # Find item
        item = db.query(ItemRecord).filter(ItemRecord.name == body.npc_item_name).first()
        db.add(TradeRecordRecord(
            proposer_type="player", proposer_id=body.player_id,
            receiver_npc_id=body.npc_id, offered_item_id=item.id if item else None,
            offered_gold=body.offered_gold, final_price=result.get("fair_price"),
            status=result.get("decision", "rejected"),
        ))

        # Update affection based on trade outcome
        decision = result.get("decision", "reject")
        delta = 3.0 if decision == "accept" else (-2.0 if decision == "reject" else 1.0)
        player.update_affection(body.npc_id, delta)
        rel = db.query(RelationshipRecord).filter(
            RelationshipRecord.subject_npc_id == body.npc_id,
            RelationshipRecord.object_type == "player",
            RelationshipRecord.object_id == body.player_id,
        ).first()
        if rel:
            rel.affection = max(0, min(100, rel.affection + delta))

        db.commit()
    finally:
        db.close()

    return TradeResponse(
        status=result.get("status", "ok"),
        decision=result.get("decision", "reject"),
        npc_reply=result.get("npc_reply", "让我再想想..."),
        fair_price=result.get("fair_price", 0),
        counter_offer=result.get("counter_offer"),
    )


@router.post("/{trade_id}/accept")
async def accept_trade(request: Request, trade_id: int):
    from app.storage.database import SessionLocal
    db = SessionLocal()
    try:
        record = db.query(TradeRecordRecord).filter(TradeRecordRecord.id == trade_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Trade not found")
        record.status = "accepted"
        db.commit()
        return {"status": "ok", "trade_id": trade_id, "status_new": "accepted"}
    finally:
        db.close()


@router.post("/{trade_id}/reject")
async def reject_trade(request: Request, trade_id: int):
    from app.storage.database import SessionLocal
    db = SessionLocal()
    try:
        record = db.query(TradeRecordRecord).filter(TradeRecordRecord.id == trade_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Trade not found")
        record.status = "rejected"
        db.commit()
        return {"status": "ok", "trade_id": trade_id, "status_new": "rejected"}
    finally:
        db.close()
