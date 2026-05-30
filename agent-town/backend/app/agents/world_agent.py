from __future__ import annotations

from app.core.agent import Agent
from app.core.config import AgentConfig
from app.core.message import Message, Role
from app.llm.base import BaseLLM


class WorldAgent(Agent):
    """WorldAgent — 管理世界时间、NPC 日程、记忆整合

    推进时间 → 更新 NPC 位置 → 触发夜间记忆整合
    """

    def __init__(self, llm: BaseLLM, config: AgentConfig | None = None):
        super().__init__(name="world", config=config or AgentConfig(), llm=llm)

    async def run(self, input_message: Message) -> Message:
        return Message(role=Role.ASSISTANT, content="ok", metadata={})

    async def advance_time(self, hours: int = 1) -> dict:
        """推进世界时间，返回新状态和是否需要整合记忆"""
        if "world" not in self.tools:
            return {"status": "error", "message": "World tool not registered"}

        result = await self.tools["world"].run(action="advance_time", hours=hours)
        return result

    async def get_world_state(self) -> dict:
        """获取当前世界状态"""
        if "world" not in self.tools:
            return {"status": "error", "message": "World tool not registered"}
        return await self.tools["world"].run(action="get_state")

    async def get_all_npc_locations(self, time_slot: str = "08:00") -> dict:
        """获取所有 NPC 当前所在地点"""
        if "schedule" not in self.tools:
            return {"status": "error", "message": "Schedule tool not registered"}
        return await self.tools["schedule"].run(action="get_all_current", time_slot=time_slot)

    async def get_npc_location(self, npc_name: str, time_slot: str = "08:00") -> dict:
        """获取指定 NPC 当前所在地点"""
        if "schedule" not in self.tools:
            return {"status": "error", "message": "Schedule tool not registered"}
        return await self.tools["schedule"].run(
            action="get_location_at", npc_name=npc_name, time_slot=time_slot,
        )

    async def consolidate_all_memories(self, current_day: int, npc_ids: list[int]) -> dict:
        """夜间整合所有 NPC 记忆"""
        if "memory" not in self.tools:
            return {"status": "error", "message": "Memory tool not registered"}

        results = {}
        for npc_id in npc_ids:
            r = await self.tools["memory"].run(action="consolidate", npc_id=npc_id, current_day=current_day)
            results[npc_id] = r
        return {"status": "ok", "results": results}

    async def get_schedule(self, npc_name: str) -> dict:
        """获取 NPC 日程"""
        if "schedule" not in self.tools:
            return {"status": "error", "message": "Schedule tool not registered"}
        return await self.tools["schedule"].run(action="get_schedule", npc_name=npc_name)
