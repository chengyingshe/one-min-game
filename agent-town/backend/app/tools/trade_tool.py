from app.core.tool import Tool
from app.llm.base import BaseLLM


class TradeTool(Tool):
    """交易工具 — NPC 评估交易提议并做出决策"""

    name = "trade"
    description = "NPC 评估玩家交易提议：接受、拒绝或还价"

    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def get_parameters(self) -> dict:
        return {
            "npc_name": {"type": "string"},
            "npc_personality": {"type": "object"},
            "npc_speaking_style": {"type": "string"},
            "current_emotion": {"type": "string"},
            "relationship_affection": {"type": "number"},
            "offered_item_name": {"type": "string"},
            "offered_gold": {"type": "number"},
            "npc_item_name": {"type": "string"},
            "npc_item_price": {"type": "number"},
        }

    async def run(self, **kwargs) -> dict:
        npc_name = kwargs["npc_name"]
        tags = kwargs.get("npc_personality", {}).get("tags", [])
        emotion = kwargs.get("current_emotion", "neutral")
        affection = kwargs.get("relationship_affection", 50)
        offered_item = kwargs.get("offered_item_name", "一些金币")
        offered_gold = kwargs.get("offered_gold", 0)
        npc_item = kwargs.get("npc_item_name", "一件物品")
        npc_price = kwargs.get("npc_item_price", 50)

        affection_bonus = 1 - (affection / 100) * 0.4
        fair_price = npc_price * affection_bonus
        total_offer = offered_gold + (npc_price * 0.5 if offered_item else 0)
        ratio = total_offer / fair_price if fair_price > 0 else 2

        if ratio >= 1.3:
            decision = "accept"
            decision_text = "这个价格很公道"
        elif ratio >= 0.7:
            decision = "counter"
            counter = round(fair_price * (1.1 - affection / 500), 1)
            decision_text = f"还价 {counter} 金币"
        else:
            decision = "reject"
            decision_text = "这价格太低了"

        system_prompt = f"""你是{npc_name}，性格：{'、'.join(tags)}。当前心情：{emotion}。
有人想用"{offered_item}+{offered_gold}金币"换你的"{npc_item}（价值{npc_price}金币）"。
市场分析：合理价约{fair_price:.0f}金币，对方出价比例{ratio:.1%}。
建议：{decision_text}。
请用你的角色口吻回复（1-2句话）。"""

        try:
            reply = await self.llm.chat(
                [{"role": "user", "content": system_prompt}],
                temperature=0.7, max_tokens=200,
            )
            return {
                "status": "ok", "decision": decision, "npc_reply": reply.strip(),
                "fair_price": round(fair_price, 1), "counter_offer": round(fair_price, 1) if decision == "counter" else None,
            }
        except Exception as e:
            fallbacks = {
                "accept": {"林黛玉": "这交易倒也公允，我应了。", "孙悟空": "俺老孙觉得行！拿着吧！", "张飞": "好！这买卖做得！"},
                "reject": {"林黛玉": "这价...恕难从命。", "孙悟空": "你这也太少了，不换！", "张飞": "不行不行，再加点！"},
                "counter": {"林黛玉": "你若再加些，我便应了。", "孙悟空": "再添点，俺老孙就换！", "张飞": "这样，你再给{:.0f}金币！"},
            }
            fallback = fallbacks.get(decision, {}).get(npc_name, decision_text)
            if decision == "counter":
                fallback = fallback.format(fair_price)
            return {"status": "fallback", "decision": decision, "npc_reply": fallback, "error": str(e)}
