const BASE = "";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Game
  seed: () =>
    request<{ status: string; message: string }>("/api/game/seed", {
      method: "POST",
    }),
  getGameState: () => request<import("./types").GameState>("/api/game/state"),
  advanceTime: (hours: number) =>
    request<Record<string, unknown>>("/api/game/advance-time", {
      method: "POST",
      body: JSON.stringify({ hours }),
    }),

  // Player
  createPlayer: (name: string, identity: string) =>
    request<import("./types").Player>("/api/player", {
      method: "POST",
      body: JSON.stringify({ name, identity }),
    }),
  getPlayer: (id: number) =>
    request<import("./types").Player>(`/api/player/${id}`),

  // NPCs
  listNpcs: () => request<import("./types").NPC[]>("/api/npcs"),
  getNpc: (id: number) => request<import("./types").NPC>(`/api/npcs/${id}`),

  // Dialogue
  sendDialogue: (
    player_id: number,
    npc_id: number,
    content: string,
    location: string,
  ) =>
    request<import("./types").DialogueResponse>("/api/dialogue", {
      method: "POST",
      body: JSON.stringify({ player_id, npc_id, content, location }),
    }),
  getHistory: (npc_id: number, player_id: number) =>
    request<{ history: import("./types").DialogueMessage[] }>(
      `/api/dialogue/history/${npc_id}?player_id=${player_id}`,
    ),

  // Trade
  proposeTrade: (data: {
    player_id: number;
    npc_id: number;
    offered_item_name: string;
    offered_gold: number;
    npc_item_name: string;
    npc_item_price: number;
  }) =>
    request<import("./types").TradeResult>("/api/trade/propose", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Memories
  getMemories: (npc_id: number, query?: string) =>
    request<{ memories: import("./types").MemoryEntry[] }>(
      `/api/memories/${npc_id}?query=${encodeURIComponent(query || "")}`,
    ),
  getMemoryTimeline: (npc_id: number) =>
    request<{ memories: import("./types").MemoryEntry[] }>(
      `/api/memories/${npc_id}/timeline`,
    ),

  // Relationships
  getRelationships: (player_id: number) =>
    request<{ relationships: Record<number, number> }>(
      `/api/relationships/player/${player_id}`,
    ),
};
