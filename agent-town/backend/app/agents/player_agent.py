from __future__ import annotations

from app.core.agent import Agent
from app.core.config import AgentConfig
from app.core.message import Message, Role
from app.llm.base import BaseLLM


class PlayerAgent(Agent):
    """PlayerAgent — 玩家状态管理

    跟踪玩家的位置、物品、金币和 NPC 关系。轻量级实现，无 LLM 调用。
    """

    def __init__(self, player_id: int, player_data: dict, llm: BaseLLM | None = None, config: AgentConfig | None = None):
        super().__init__(
            name=player_data.get("name", "玩家"),
            config=config or AgentConfig(),
            llm=llm or _NoopLLM(),
        )
        self.player_id = player_id
        self.identity = player_data.get("identity", "行脚商人")
        self.current_location = player_data.get("current_location", "茶馆")
        self.wealth = player_data.get("wealth", 100.0)
        self.inventory: list[dict] = player_data.get("inventory", [])
        self.relationships: dict[int, float] = player_data.get("relationships", {})  # npc_id -> affection

    async def run(self, input_message: Message) -> Message:
        """处理系统指令：移动、获取/使用物品等"""
        return Message(role=Role.ASSISTANT, content="ok", metadata={})

    def move_to(self, location: str):
        self.current_location = location

    def add_gold(self, amount: float):
        self.wealth += amount

    def remove_gold(self, amount: float) -> bool:
        if self.wealth >= amount:
            self.wealth -= amount
            return True
        return False

    def add_item(self, item: dict):
        self.inventory.append(item)

    def remove_item(self, item_name: str) -> dict | None:
        for i, item in enumerate(self.inventory):
            if item.get("name") == item_name:
                return self.inventory.pop(i)
        return None

    def get_affection(self, npc_id: int) -> float:
        return self.relationships.get(npc_id, 50.0)

    def update_affection(self, npc_id: int, delta: float):
        current = self.relationships.get(npc_id, 50.0)
        self.relationships[npc_id] = max(0, min(100, current + delta))

    def to_dict(self) -> dict:
        return {
            "id": self.player_id,
            "name": self.name,
            "identity": self.identity,
            "current_location": self.current_location,
            "wealth": self.wealth,
            "inventory": self.inventory,
            "relationships": self.relationships,
        }


class _NoopLLM(BaseLLM):
    """PlayerAgent 不需要 LLM 调用，提供一个空实现"""

    async def chat(self, messages: list[dict], **kwargs) -> str:
        return ""

    async def embed(self, text: str) -> list[float]:
        return []
