import json

from app.core.tool import Tool
from app.llm.base import BaseLLM


class DialogueTool(Tool):
    """对话工具 — 构建 NPC 对话 prompt + 调用 LLM 生成回复"""

    name = "dialogue"
    description = "构建 NPC 角色对话 prompt，调用 LLM 生成符合角色性格的中文回复"

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def get_parameters(self) -> dict:
        return {
            "npc_name": {"type": "string"},
            "npc_source": {"type": "string"},
            "npc_personality": {"type": "object"},
            "npc_speaking_style": {"type": "string"},
            "current_emotion": {"type": "string"},
            "current_location": {"type": "string"},
            "relationship_affection": {"type": "number"},
            "memories": {"type": "array"},
            "player_message": {"type": "string"},
        }

    async def run(self, **kwargs) -> dict:
        # NPC-to-NPC 模式
        if kwargs.get("mode") == "npc_to_npc":
            return await self._run_npc_to_npc(**kwargs)

        npc_name = kwargs["npc_name"]
        npc_source = kwargs.get("npc_source", "")
        personality_tags = kwargs.get("npc_personality", {}).get("tags", [])
        speaking_style = kwargs.get("npc_speaking_style", "")
        emotion = kwargs.get("current_emotion", "neutral")
        location = kwargs.get("current_location", "茶馆")
        affection = kwargs.get("relationship_affection", 50)
        memories = kwargs.get("memories", [])
        player_message = kwargs.get("player_message", "")

        system_prompt = self._build_system_prompt(
            npc_name, npc_source, personality_tags, speaking_style, emotion, location, affection, memories
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": player_message},
        ]

        try:
            reply = await self.llm.chat(messages, temperature=0.85, max_tokens=400)
            return {"status": "ok", "reply": reply.strip()}
        except Exception as e:
            return {"status": "fallback", "reply": self._fallback(npc_name), "error": str(e)}

    def _build_system_prompt(self, name, source, tags, style, emotion, location, affection, memories) -> str:
        tags_str = "、".join(tags) if tags else ""
        emotion_cn = {"happy": "开心", "sad": "悲伤", "angry": "愤怒", "tired": "疲惫",
                      "lonely": "孤独", "satisfied": "满足", "neutral": "平静"}.get(emotion, "平静")

        affection_desc = "陌生"
        if affection >= 80: affection_desc = "非常喜欢"
        elif affection >= 60: affection_desc = "有好感"
        elif affection >= 40: affection_desc = "一般"
        elif affection >= 20: affection_desc = "不太喜欢"
        elif affection >= 0: affection_desc = "反感"

        memory_text = ""
        if memories:
            short = [m for m in memories if m.get("tier") == "short_term"]
            medium = [m for m in memories if m.get("tier") == "medium_term"]
            long_m = [m for m in memories if m.get("tier") == "long_term"]

            if short:
                memory_text += "最近的记忆：\n" + "\n".join(f"- {m['event']}（{m['emotion']}）" for m in short[:3]) + "\n\n"
            if medium:
                memory_text += "你对TA的印象：\n" + "\n".join(f"- {m['event']}" for m in medium[:2]) + "\n\n"
            if long_m:
                memory_text += "你们之间重要的事：\n" + "\n".join(f"- {m['event']}（{m['emotion']}）" for m in long_m[:2]) + "\n\n"

        return f"""你是{name}，来自《{source}》，生活在"时空杂货镇"的{location}。

性格特点：{tags_str}
说话风格：{style}
当前心情：{emotion_cn}

对你面前这个人的感觉：{affection_desc}
{memory_text}
规则：
- 你不是AI助手，你是一个真实的人，不要提及自己是AI或语言模型
- 回复用2-4句话，符合你的性格和说话风格
- 如果你喜欢对方，语气会温和；如果不喜欢，会用符合你性格的方式表达不满
- 当前心情会影响你的回复语气

现在，这个人对你说："""

    def _fallback(self, name: str) -> str:
        fallbacks = {
            "林黛玉": "...（轻叹一声，没有言语）",
            "孙悟空": "俺老孙正忙着呢！改日再说！",
            "张飞": "嗯？你说什么？哈哈哈！",
        }
        return fallbacks.get(name, "...（沉默不语）")

    async def _run_npc_to_npc(self, **kwargs) -> dict:
        """生成两个 NPC 之间的对话（2-4 轮）"""
        npc_a = kwargs["npc_a"]
        npc_b = kwargs["npc_b"]
        location = kwargs.get("location", "茶馆")
        memories_a = kwargs.get("memories_a", [])
        memories_b = kwargs.get("memories_b", [])

        try:
            lines = []
            # 第一轮：A 先说
            prompt_a = self._build_npc_dialogue_prompt(npc_a, npc_b, location, memories_a, "开始对话")
            messages_a = [
                {"role": "system", "content": prompt_a},
                {"role": "user", "content": f"你遇到了{npc_b['name']}，想和TA打个招呼或聊几句。"},
            ]
            reply_a = await self.llm.chat(messages_a, temperature=0.9, max_tokens=200)
            lines.append({"speaker": npc_a["name"], "content": reply_a.strip()})

            # 第二轮：B 回应
            prompt_b = self._build_npc_dialogue_prompt(npc_b, npc_a, location, memories_b, f"{npc_a['name']}对你说：{reply_a.strip()}")
            messages_b = [
                {"role": "system", "content": prompt_b},
                {"role": "user", "content": f"{npc_a['name']}对你说：{reply_a.strip()}"},
            ]
            reply_b = await self.llm.chat(messages_b, temperature=0.9, max_tokens=200)
            lines.append({"speaker": npc_b["name"], "content": reply_b.strip()})

            # 第三轮：A 继续说
            context = f"你刚说了：{reply_a.strip()}。{npc_b['name']}回应：{reply_b.strip()}"
            prompt_a2 = self._build_npc_dialogue_prompt(npc_a, npc_b, location, memories_a, context)
            messages_a2 = [
                {"role": "system", "content": prompt_a2},
                {"role": "user", "content": context + "\n请继续回复（1-2句）。"},
            ]
            reply_a2 = await self.llm.chat(messages_a2, temperature=0.9, max_tokens=200)
            lines.append({"speaker": npc_a["name"], "content": reply_a2.strip()})

            return {"status": "ok", "lines": lines}
        except Exception as e:
            return {"status": "error", "error": str(e), "lines": []}

    def _build_npc_dialogue_prompt(self, speaker: dict, listener: dict, location: str, memories: list, context: str) -> str:
        """构建 NPC 间对话的 system prompt"""
        tags = speaker.get("personality", {}).get("tags", [])
        tags_str = "、".join(tags) if tags else ""
        emotion_cn = {"happy": "开心", "sad": "悲伤", "angry": "愤怒", "tired": "疲惫",
                      "lonely": "孤独", "satisfied": "满足", "neutral": "平静"}.get(speaker.get("emotion", "neutral"), "平静")

        memory_text = ""
        if memories:
            short = [m for m in memories if m.get("tier") == "short_term"]
            medium = [m for m in memories if m.get("tier") == "medium_term"]
            if short:
                memory_text += "你关于TA的最近记忆：\n" + "\n".join(f"- {m['event']}" for m in short[:2]) + "\n"
            if medium:
                memory_text += "你对TA的印象：\n" + "\n".join(f"- {m['event']}" for m in medium[:2]) + "\n"

        return f"""你是{speaker['name']}，来自《{speaker['source']}》。你正在时空杂货镇的{location}。
你遇到了{listener['name']}（来自《{listener['source']}》）。

你的性格：{tags_str}
你的说话风格：{speaker.get('speaking_style', '')}
你当前的心情：{emotion_cn}
{memory_text}
规则：
- 你不是AI助手，你是一个真实的人
- 回复用1-2句话，符合你的性格和说话风格
- 自然地回应对方，像朋友间的日常聊天
- 当前心情会影响你的语气"""
