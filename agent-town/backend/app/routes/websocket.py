import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/game")
async def game_websocket(websocket: WebSocket):
    await websocket.accept()
    sim = websocket.app.state.simulation_engine
    sim.subscribe(websocket)

    try:
        # 发送初始状态
        await _send_initial_state(websocket, websocket.app)

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue

            action = msg.get("action")

            if action == "pause":
                sim.pause()
                await websocket.send_json({"type": "status", "paused": True})

            elif action == "resume":
                sim.resume()
                await websocket.send_json({"type": "status", "paused": False})

            elif action == "set_speed":
                interval = msg.get("interval", 5)
                sim.set_speed(interval)
                await websocket.send_json({"type": "status", "tick_interval": interval})

    except WebSocketDisconnect:
        pass
    finally:
        sim.unsubscribe(websocket)


async def _send_initial_state(ws: WebSocket, app):
    from app.storage.database import SessionLocal
    from app.storage.db_models import NpcRecord, WorldStateRecord

    db = SessionLocal()
    try:
        # 世界状态
        day_rec = db.query(WorldStateRecord).filter(WorldStateRecord.key == "current_day").first()
        time_rec = db.query(WorldStateRecord).filter(WorldStateRecord.key == "current_time").first()
        current_day = json.loads(day_rec.value_json) if day_rec else 1
        current_time = json.loads(time_rec.value_json) if time_rec else "08:00"

        # NPC 位置
        npcs = db.query(NpcRecord).all()
        positions = [
            {
                "id": n.id, "name": n.name,
                "pos_x": n.pos_x, "pos_y": n.pos_y,
                "current_location": n.current_location,
                "target_location": n.target_location,
                "is_moving": n.is_moving,
                "avatar_emoji": n.avatar_emoji,
                "current_emotion": n.current_emotion,
            }
            for n in npcs
        ]

        await ws.send_json({
            "type": "init",
            "current_day": current_day,
            "current_time": current_time,
            "positions": positions,
        })
    finally:
        db.close()
