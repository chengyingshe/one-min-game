from __future__ import annotations

from app.core.agent import Agent
from app.core.config import AgentConfig
from app.core.message import Message, Role
from app.llm.base import BaseLLM


class NPCAgent(Agent):
    """NPC Agent — 封装角色的对话、记忆、情绪、交易决策

    每个 NPC 一个实例。处理玩家输入: 检索记忆 → 获取情绪 → 生成回复 → 存储记忆 → 更新状态。
    """

    def __init__(self, npc_id: int, npc_data: dict, llm: BaseLLM, config: AgentConfig | None = None):
        super().__init__(
            name=npc_data["name"],
            config=config or AgentConfig(),
            llm=llm,
        )
        self.npc_id = npc_id
        self.npc_data = npc_data
        self.personality = npc_data.get("personality", {})
        self.current_emotion = npc_data.get("current_emotion", "neutral")
        self.dialogue_history: list[Message] = []

    async def run(self, input_message: Message) -> Message:
        """处理玩家输入 → 检索记忆 → 生成回复 → 更新状态"""
        player_content = input_message.content
        player_metadata = input_message.metadata

        # 1. 检索相关记忆
        memories = []
        if "memory" in self.tools:
            result = await self.tools["memory"].run(
                action="search", npc_id=self.npc_id, query=player_content, limit=5,
            )
            memories = result.get("memories", [])

        # 2. 获取当前情绪
        emotion = self.current_emotion
        if "emotion" in self.tools:
            emotion_result = await self.tools["emotion"].run(
                action="get", npc_id=self.npc_id,
            )
            emotion = emotion_result.get("emotion", self.current_emotion)

        # 3. 获取当前地点
        location = player_metadata.get("location", self.npc_data.get("current_location", "茶馆"))

        # 4. 获取好感度
        affection = player_metadata.get("affection", 50)

        # 5. 生成对话回复
        reply_text = ""
        if "dialogue" in self.tools:
            dialogue_result = await self.tools["dialogue"].run(
                npc_name=self.name,
                npc_source=self.npc_data.get("source", ""),
                npc_personality=self.personality,
                npc_speaking_style=self.npc_data.get("speaking_style", ""),
                current_emotion=emotion,
                current_location=location,
                relationship_affection=affection,
                memories=memories,
                player_message=player_content,
            )
            reply_text = dialogue_result.get("reply", "")

        # 6. 存储新记忆
        if "memory" in self.tools:
            await self.tools["memory"].run(
                action="store",
                npc_id=self.npc_id,
                event=f"玩家对我说: {player_content}",
                emotion=emotion,
                importance=self._estimate_importance(player_content, reply_text),
                tier="short_term",
                participants=["player"],
                day_number=player_metadata.get("day_number", 1),
            )

        # 7. 更新好感度
        if "emotion" in self.tools:
            delta = self.tools["emotion"].compute_affection_delta(player_content, self.personality)
            # 传递 delta 信息到 metadata 中，让调用方更新 relationship
            pass  # affection update handled by route layer after dialogue

        self.dialogue_history.append(input_message)
        reply = Message(role=Role.ASSISTANT, content=reply_text, metadata={
            "emotion": emotion,
            "memories_used": len(memories),
            "affection_delta": self.tools["emotion"].compute_affection_delta(player_content, self.personality) if "emotion" in self.tools else 0,
        })
        self.dialogue_history.append(reply)

        # 裁剪历史
        if len(self.dialogue_history) > self.config.max_history * 2:
            self.dialogue_history = self.dialogue_history[-self.config.max_history * 2:]

        return reply

    async def evaluate_trade(self, player_offer: dict) -> dict:
        """评估交易提议"""
        if "trade" not in self.tools:
            return {"status": "error", "message": "Trade tool not registered"}

        affection = player_offer.get("affection", 50)
        result = await self.tools["trade"].run(
            npc_name=self.name,
            npc_personality=self.personality,
            npc_speaking_style=self.npc_data.get("speaking_style", ""),
            current_emotion=self.current_emotion,
            relationship_affection=affection,
            offered_item_name=player_offer.get("offered_item_name", ""),
            offered_gold=player_offer.get("offered_gold", 0),
            npc_item_name=player_offer.get("npc_item_name", ""),
            npc_item_price=player_offer.get("npc_item_price", 0),
        )
        return result

    def _estimate_importance(self, player_msg: str, reply: str) -> float:
        """简单的重要性评估：基于消息长度和关键词"""
        importance = 30.0
        if len(player_msg) > 20:
            importance += 10
        key_words = ["秘密", "爱", "恨", "宝物", "救命", "交易", "离别", "重逢"]
        for w in key_words:
            if w in player_msg:
                importance += 15
        return min(100, importance)
