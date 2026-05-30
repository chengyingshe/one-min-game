export interface NPC {
  id: number;
  name: string;
  source: string;
  occupation: string;
  personality: Record<string, unknown>;
  current_location: string;
  current_emotion: string;
  speaking_style: string;
  avatar_emoji: string;
}

export interface Player {
  id: number;
  name: string;
  identity: string;
  current_location: string;
  wealth: number;
  inventory: Item[];
  relationships: Record<number, number>;
}

export interface Item {
  name: string;
  type: string;
  base_price: number;
  description: string;
}

export interface GameState {
  current_day: number;
  current_time: string;
  npcs: NPC[];
  locations: Location[];
}

export interface Location {
  id: number;
  name: string;
  display_name: string;
  description: string;
  type: string;
  emoji: string;
}

export interface DialogueMessage {
  speaker_type: "player" | "npc";
  speaker_id: number;
  content: string;
  location: string;
  day_number: number;
  created_at?: string;
}

export interface MemoryEntry {
  id: string;
  event: string;
  emotion: string;
  importance: number;
  tier: "short_term" | "medium_term" | "long_term";
  similarity?: number;
  day_number?: number;
}

export interface TradeResult {
  status: string;
  decision: "accept" | "counter" | "reject";
  npc_reply: string;
  fair_price: number;
  counter_offer: number | null;
}

export interface DialogueResponse {
  npc_id: number;
  npc_name: string;
  reply: string;
  emotion: string;
  location: string;
  affection_delta: number;
  memories_used: number;
}

// ── Simulation types ──

export interface NpcPosition {
  id: number;
  name: string;
  pos_x: number;
  pos_y: number;
  current_location: string;
  target_location: string;
  is_moving: boolean;
  avatar_emoji: string;
  current_emotion: string;
}

export interface NpcDialogueLine {
  speaker: string;
  content: string;
}

export interface NpcConversation {
  location: string;
  npc_a: string;
  npc_b: string;
  lines: NpcDialogueLine[];
}

export interface WsTickMessage {
  type: "tick" | "init" | "status";
  tick?: number;
  positions?: NpcPosition[];
  dialogues?: NpcConversation[];
  current_day?: number;
  current_time?: string;
  paused?: boolean;
  tick_interval?: number;
}
