from __future__ import annotations

import uuid
from datetime import datetime, timezone

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
)

from app.core.tool import Tool
from app.llm.base import BaseLLM
from app.storage.qdrant_client import COLLECTION_NAME, get_qdrant


class MemoryTool(Tool):
    """记忆工具 — 管理 NPC 的三层记忆系统（短期/中期/长期）

    Qdrant 存储: 向量嵌入 + payload
    检索: 语义相似度 × 0.6 + 重要性 × 0.4 加权排序
    """

    name = "memory"
    description = "管理 NPC 的三层记忆系统（短期/中期/长期），支持语义检索、存储、整合和遗忘"

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.qdrant = get_qdrant()

    def get_parameters(self) -> dict:
        return {
            "action": {
                "type": "string",
                "enum": ["search", "store", "consolidate", "forget"],
                "description": "操作类型",
            },
            "npc_id": {"type": "integer", "description": "NPC ID"},
            "query": {"type": "string", "description": "搜索查询文本"},
            "event": {"type": "string", "description": "记忆事件描述"},
            "emotion": {"type": "string", "description": "关联情绪"},
            "importance": {"type": "number", "description": "重要性 0-100"},
            "participants": {"type": "array", "description": "参与者列表"},
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action", "search")
        if action == "search":
            return await self._search(kwargs["npc_id"], kwargs.get("query", ""), kwargs.get("limit", 5))
        elif action == "store":
            return await self._store(
                kwargs["npc_id"], kwargs["event"], kwargs.get("emotion", "neutral"),
                kwargs.get("importance", 30.0), kwargs.get("tier", "short_term"),
                kwargs.get("participants", []), kwargs.get("day_number", 1),
            )
        elif action == "consolidate":
            return await self._consolidate(kwargs["npc_id"], kwargs.get("current_day", 1))
        elif action == "forget":
            return await self._forget(kwargs["npc_id"], kwargs.get("tier", "short_term"))
        return {"status": "error", "message": f"Unknown action: {action}"}

    async def _search(self, npc_id: int, query: str, limit: int = 5) -> dict:
        embedding = await self.llm.embed(query)

        response = self.qdrant.client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            query_filter=Filter(must=[FieldCondition(key="npc_id", match=MatchValue(value=npc_id))]),
            limit=limit * 2,
            with_payload=True,
        )

        scored = sorted(
            response.points,
            key=lambda r: (r.score or 0) * 0.6 + (r.payload.get("importance", 0) if r.payload else 0) / 100 * 0.4,
            reverse=True,
        )
        memories = []
        for r in scored[:limit]:
            p = r.payload or {}
            memories.append({
                "id": r.id,
                "event": p.get("event", ""),
                "emotion": p.get("emotion", "neutral"),
                "importance": p.get("importance", 0),
                "tier": p.get("tier", "short_term"),
                "participants": p.get("participants", []),
                "day_number": p.get("day_number", 1),
                "similarity": round(r.score or 0, 3),
            })
        return {"status": "ok", "memories": memories}

    async def _store(self, npc_id: int, event: str, emotion: str, importance: float,
                     tier: str, participants: list[str], day_number: int) -> dict:
        embedding = await self.llm.embed(event)
        point_id = uuid.uuid4().hex
        self.qdrant.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "npc_id": npc_id, "event": event, "emotion": emotion,
                    "importance": importance, "tier": tier,
                    "participants": participants, "day_number": day_number,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )],
        )
        return {"status": "ok", "memory_id": point_id, "tier": tier}

    async def _consolidate(self, npc_id: int, current_day: int) -> dict:
        """夜间记忆整合: 压缩前一天短期记忆 → 生成中期印象"""
        results, _ = self.qdrant.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=[
                FieldCondition(key="npc_id", match=MatchValue(value=npc_id)),
                FieldCondition(key="tier", match=MatchValue(value="short_term")),
                FieldCondition(key="day_number", range=Range(lt=current_day)),
            ]),
            limit=50,
        )
        old_count = len(results)
        if old_count <= 10:
            return {"status": "ok", "consolidated": 0, "message": "Not enough memories to consolidate"}

        events = [p.payload.get("event", "") for p in results if p.payload]
        summary_prompt = "以下是角色在过去一天中的记忆片段，请将它们总结为 1-2 条中期印象记忆（每条 20-30 字）：\n" + "\n".join(f"- {e}" for e in events[:20])
        messages = [
            {"role": "system", "content": "你是一个记忆整合助手。请将短期记忆压缩为中期印象。"},
            {"role": "user", "content": summary_prompt},
        ]
        summary = await self.llm.chat(messages, temperature=0.4, max_tokens=300)

        old_ids = [p.id for p in results]
        if old_ids:
            self.qdrant.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=old_ids,
            )

        await self._store(npc_id, summary.strip(), "neutral", 60.0, "medium_term", [], current_day)
        return {"status": "ok", "consolidated": old_count, "summary": summary.strip()}

    async def _forget(self, npc_id: int, tier: str) -> dict:
        results, _ = self.qdrant.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=[
                FieldCondition(key="npc_id", match=MatchValue(value=npc_id)),
                FieldCondition(key="tier", match=MatchValue(value=tier)),
                FieldCondition(key="importance", range=Range(lt=20)),
            ]),
            limit=100,
        )
        old_ids = [p.id for p in results]
        if old_ids:
            self.qdrant.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=old_ids,
            )
        return {"status": "ok", "forgotten": len(old_ids)}
