from fastapi import APIRouter, HTTPException, Request, Query

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("/{npc_id}")
async def get_npc_memories(request: Request, npc_id: int, query: str = "", limit: int = 10):
    """搜索 NPC 记忆"""
    npc_agents = getattr(request.app.state, "npc_agents", [])
    npc = next((a for a in npc_agents if a.npc_id == npc_id), None)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    if "memory" not in npc.tools:
        raise HTTPException(status_code=500, detail="Memory tool not available")

    result = await npc.tools["memory"].run(
        action="search", npc_id=npc_id, query=query or "最近发生的事", limit=limit,
    )
    return {"npc_id": npc_id, "query": query, "memories": result.get("memories", [])}


@router.get("/{npc_id}/timeline")
async def get_memory_timeline(request: Request, npc_id: int, tier: str = "all", limit: int = 20):
    """获取 NPC 记忆时间线"""
    npc_agents = getattr(request.app.state, "npc_agents", [])
    npc = next((a for a in npc_agents if a.npc_id == npc_id), None)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    # Use a broad search to get memories
    result = await npc.tools["memory"].run(
        action="search", npc_id=npc_id, query="", limit=limit,
    )
    memories = result.get("memories", [])

    # Filter by tier if specified
    if tier != "all":
        memories = [m for m in memories if m.get("tier") == tier]

    # Sort by day_number desc
    memories.sort(key=lambda m: m.get("day_number", 0), reverse=True)

    return {"npc_id": npc_id, "memories": memories, "total": len(memories)}
