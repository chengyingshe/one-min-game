from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)

# 地图坐标常量（800x500 画布内各地点中心坐标）
LOCATION_COORDS: dict[str, tuple[float, float]] = {
    "茶馆": (200, 320),
    "集市": (600, 320),
    "书院": (200, 120),
    "河边": (600, 120),
}

# 同地点 NPC 对话冷却（tick 数）
CHAT_COOLDOWN_TICKS = 3


class SimulationEngine:
    """模拟引擎 — 每 tick 推进 NPC 移动和自主对话"""

    def __init__(self, npc_agents, world_agent, db_session_factory):
        self.npc_agents = npc_agents
        self.world_agent = world_agent
        self.db_session_factory = db_session_factory
        self.running = False
        self.paused = False
        self.tick_interval = 5  # seconds
        self.current_tick = 0
        self.subscribers: list[WebSocket] = []
        self._task: asyncio.Task | None = None

        # 记录 NPC 间最近对话的 tick，用于冷却
        self._chat_cooldowns: dict[tuple[int, int], int] = {}

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def set_speed(self, interval: int):
        self.tick_interval = max(1, min(30, interval))

    async def subscribe(self, ws: WebSocket):
        self.subscribers.append(ws)

    def unsubscribe(self, ws: WebSocket):
        if ws in self.subscribers:
            self.subscribers.remove(ws)

    # ── internal ──

    async def _loop(self):
        while self.running:
            if not self.paused:
                await self._tick()
            await asyncio.sleep(self.tick_interval)

    async def _tick(self):
        self.current_tick += 1
        try:
            ws = self.world_agent
            state = await ws.get_world_state()
            current_time = state.get("current_time", "08:00")

            # 1. 根据 schedule 推进 NPC 位置
            position_updates = await self._update_positions(current_time)

            # 2. 推进世界时间（每 tick +10 分钟游戏时间）
            time_result = await ws.tools["world"].advance_time(0)
            # 手动推进 10 分钟
            self._advance_minutes(10)

            # 3. 检测同地点 NPC → 触发对话
            dialogues = await self._check_npc_dialogues()

            # 4. 广播状态
            await self._broadcast({
                "type": "tick",
                "tick": self.current_tick,
                "positions": position_updates,
                "dialogues": dialogues,
            })
        except Exception as e:
            logger.error("Simulation tick error: %s", e)

    async def _update_positions(self, current_time: str) -> list[dict]:
        """根据 schedule 判断每个 NPC 应在的地点，并插值移动坐标"""
        from app.storage.database import SessionLocal
        from app.storage.db_models import NpcRecord

        schedule_tool = self.world_agent.tools.get("schedule")
        if not schedule_tool:
            return []

        schedule_result = await schedule_tool.run(action="get_all_current", time_slot=current_time)
        npc_locations = schedule_result.get("npcs", {})

        db = SessionLocal()
        updates = []
        try:
            for agent in self.npc_agents:
                name = agent.name
                expected_loc = npc_locations.get(name, {}).get("location", "茶馆")
                expected_coords = LOCATION_COORDS.get(expected_loc, (400, 250))

                npc = db.query(NpcRecord).filter(NpcRecord.name == name).first()
                if not npc:
                    continue

                # 如果需要移动到新地点
                if npc.current_location != expected_loc:
                    npc.target_location = expected_loc
                    npc.is_moving = True
                    agent.npc_data["current_location"] = expected_loc

                # 如果正在移动，向目标插值
                if npc.is_moving or npc.target_location:
                    target = LOCATION_COORDS.get(npc.target_location or expected_loc, expected_coords)
                    dx = target[0] - npc.pos_x
                    dy = target[1] - npc.pos_y
                    dist = (dx**2 + dy**2) ** 0.5

                    if dist < 5:
                        # 已到达
                        npc.pos_x = target[0]
                        npc.pos_y = target[1]
                        npc.current_location = npc.target_location or expected_loc
                        npc.target_location = ""
                        npc.is_moving = False
                    else:
                        # 每 tick 移动 25% 的剩余距离
                        step = 0.25
                        npc.pos_x += dx * step
                        npc.pos_y += dy * step

                db.commit()
                updates.append({
                    "id": npc.id,
                    "name": npc.name,
                    "pos_x": npc.pos_x,
                    "pos_y": npc.pos_y,
                    "current_location": npc.current_location,
                    "target_location": npc.target_location,
                    "is_moving": npc.is_moving,
                    "avatar_emoji": npc.avatar_emoji,
                })
        finally:
            db.close()

        return updates

    async def _check_npc_dialogues(self) -> list[dict]:
        """检测同地点 NPC 对并触发对话"""
        from app.storage.database import SessionLocal
        from app.storage.db_models import NpcRecord

        db = SessionLocal()
        dialogues = []
        try:
            npcs = db.query(NpcRecord).all()
            # 按地点分组（排除正在移动的）
            loc_groups: dict[str, list[NpcRecord]] = {}
            for npc in npcs:
                if not npc.is_moving and npc.current_location:
                    loc_groups.setdefault(npc.current_location, []).append(npc)

            for loc, group in loc_groups.items():
                if len(group) < 2:
                    continue
                # 随机选一对
                pair = random.sample(group, 2)
                a, b = pair[0], pair[1]
                key = (min(a.id, b.id), max(a.id, b.id))

                # 检查冷却
                last = self._chat_cooldowns.get(key, 0)
                if self.current_tick - last < CHAT_COOLDOWN_TICKS:
                    continue

                # 触发对话
                conv = await self._generate_npc_dialogue(a, b, loc)
                if conv:
                    self._chat_cooldowns[key] = self.current_tick
                    dialogues.append(conv)
                    break  # 每 tick 最多 1 场对话
        finally:
            db.close()

        return dialogues

    async def _generate_npc_dialogue(self, npc_a: Any, npc_b: Any, location: str) -> dict | None:
        """让两个 NPC 生成一段对话"""
        from app.storage.database import SessionLocal
        from app.storage.db_models import DialogueHistoryRecord

        agent_a = next((a for a in self.npc_agents if a.npc_id == npc_a.id), None)
        agent_b = next((a for a in self.npc_agents if a.npc_id == npc_b.id), None)
        if not agent_a or not agent_b:
            return None

        dialogue_tool = agent_a.tools.get("dialogue")
        memory_tool = agent_a.tools.get("memory")
        if not dialogue_tool:
            return None

        # 获取双方记忆
        memories_a, memories_b = [], []
        if memory_tool:
            r1 = await memory_tool.run(action="search", npc_id=npc_a.id, query=npc_b.name, limit=3)
            memories_a = r1.get("memories", [])
            r2 = await memory_tool.run(action="search", npc_id=npc_b.id, query=npc_a.name, limit=3)
            memories_b = r2.get("memories", [])

        # 生成对话
        result = await dialogue_tool.run(
            mode="npc_to_npc",
            npc_a={
                "name": npc_a.name, "source": npc_a.source,
                "personality": json.loads(npc_a.personality_json) if isinstance(npc_a.personality_json, str) else npc_a.personality_json,
                "speaking_style": npc_a.speaking_style,
                "emotion": npc_a.current_emotion,
            },
            npc_b={
                "name": npc_b.name, "source": npc_b.source,
                "personality": json.loads(npc_b.personality_json) if isinstance(npc_b.personality_json, str) else npc_b.personality_json,
                "speaking_style": npc_b.speaking_style,
                "emotion": npc_b.current_emotion,
            },
            memories_a=memories_a,
            memories_b=memories_b,
            location=location,
        )

        if result.get("status") != "ok":
            return None

        lines = result.get("lines", [])

        # 存入数据库
        db = SessionLocal()
        try:
            ws = await self.world_agent.get_world_state()
            day_number = ws.get("current_day", 1)
            for line in lines:
                speaker_id = npc_a.id if line["speaker"] == npc_a.name else npc_b.id
                listener_id = npc_b.id if speaker_id == npc_a.id else npc_a.id
                db.add(DialogueHistoryRecord(
                    speaker_type="npc", speaker_id=speaker_id,
                    listener_type="npc", listener_id=listener_id,
                    content=line["content"], location=location, day_number=day_number,
                ))
            db.commit()
        finally:
            db.close()

        # 存储记忆
        if memory_tool:
            ws = await self.world_agent.get_world_state()
            day_number = ws.get("current_day", 1)
            conv_summary = f"在{location}和{npc_b.name}聊天"
            await memory_tool.run(
                action="store", npc_id=npc_a.id,
                event=conv_summary, emotion="neutral",
                importance=40.0, tier="short_term",
                participants=[npc_b.name], day_number=day_number,
            )
            conv_summary_b = f"在{location}和{npc_a.name}聊天"
            await memory_tool.run(
                action="store", npc_id=npc_b.id,
                event=conv_summary_b, emotion="neutral",
                importance=40.0, tier="short_term",
                participants=[npc_a.name], day_number=day_number,
            )

        return {
            "location": location,
            "npc_a": npc_a.name,
            "npc_b": npc_b.name,
            "lines": lines,
        }

    def _advance_minutes(self, minutes: int):
        """推进游戏时间（分钟）"""
        from app.storage.database import SessionLocal
        from app.storage.db_models import WorldStateRecord

        db = SessionLocal()
        try:
            day_rec = db.query(WorldStateRecord).filter(WorldStateRecord.key == "current_day").first()
            time_rec = db.query(WorldStateRecord).filter(WorldStateRecord.key == "current_time").first()
            if not day_rec or not time_rec:
                return

            day = json.loads(day_rec.value_json)
            time_str = time_rec.value_json.strip('"')
            h, m = map(int, time_str.split(":"))
            total = h * 60 + m + minutes
            new_day = day
            while total >= 1440:
                total -= 1440
                new_day += 1
            new_h = total // 60
            new_m = total % 60
            day_rec.value_json = json.dumps(new_day)
            time_rec.value_json = json.dumps(f"{new_h:02d}:{new_m:02d}")
            db.commit()
        finally:
            db.close()

    async def _broadcast(self, message: dict):
        dead = []
        for ws in self.subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.subscribers.remove(ws)
