from sqlalchemy.orm import Session

from app.core.tool import Tool


class EmotionTool(Tool):
    """情绪工具 — 管理 NPC 情绪和好感度

    SQLite 存储关系数据, emotions 在内存中维护
    """

    name = "emotion"
    description = "管理 NPC 当前情绪和好感度，计算对话/交易后的情感变化"

    EMOTIONS = ["happy", "sad", "angry", "tired", "lonely", "satisfied", "neutral"]
    _npc_emotions: dict[int, str] = {}

    def get_parameters(self) -> dict:
        return {
            "action": {"type": "string", "enum": ["get", "update", "set"]},
            "npc_id": {"type": "integer"},
            "emotion": {"type": "string"},
            "affection_delta": {"type": "number"},
        }

    def set_emotion(self, npc_id: int, emotion: str):
        self._npc_emotions[npc_id] = emotion

    def get_emotion(self, npc_id: int) -> str:
        return self._npc_emotions.get(npc_id, "neutral")

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action", "get")
        npc_id = kwargs["npc_id"]

        if action == "get":
            return {"status": "ok", "npc_id": npc_id, "emotion": self.get_emotion(npc_id)}

        elif action == "set":
            emotion = kwargs.get("emotion", "neutral")
            self.set_emotion(npc_id, emotion)
            return {"status": "ok", "npc_id": npc_id, "emotion": emotion}

        elif action == "update":
            return {"status": "ok", "npc_id": npc_id, "emotion": self.get_emotion(npc_id)}

        return {"status": "error", "message": f"Unknown action: {action}"}

    def compute_affection_delta(self, player_message: str, npc_personality: dict) -> float:
        """简单的基于关键词的好感度变化计算"""
        delta = 1.0
        msg = player_message.lower()

        positive_words = ["谢谢", "你好", "真厉害", "佩服", "美丽", "聪明", "善良", "好", "喜欢", "帮"]
        negative_words = ["滚", "讨厌", "蠢", "笨", "烦", "恶心", "别烦我", "滚开", "垃圾"]
        compliment_words = ["诗", "才华", "美", "聪慧", "温柔", "写得真好"]

        for w in positive_words:
            if w in msg:
                delta += 2
        for w in negative_words:
            if w in msg:
                delta -= 5
        for w in compliment_words:
            if w in msg:
                delta += 3

        agreeableness = npc_personality.get("agreeableness", 50)
        delta *= (agreeableness / 50)

        return round(max(-10, min(10, delta)), 1)
