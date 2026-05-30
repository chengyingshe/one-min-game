export const NPC_META: Record<string, { emoji: string; color: string }> = {
  林黛玉: { emoji: "🌸", color: "pink" },
  孙悟空: { emoji: "🐵", color: "amber" },
  张飞: { emoji: "💪", color: "red" },
};

export const LOCATION_META: Record<string, { emoji: string; display: string }> =
  {
    teahouse: { emoji: "🍵", display: "茶馆" },
    market: { emoji: "🏮", display: "集市" },
    academy: { emoji: "📚", display: "书院" },
    riverside: { emoji: "🌿", display: "河边" },
  };

export const EMOTION_MAP: Record<string, { label: string; emoji: string }> = {
  happy: { label: "开心", emoji: "😊" },
  sad: { label: "悲伤", emoji: "😢" },
  angry: { label: "愤怒", emoji: "😠" },
  tired: { label: "疲惫", emoji: "😴" },
  lonely: { label: "孤独", emoji: "🥺" },
  satisfied: { label: "满足", emoji: "😌" },
  neutral: { label: "平静", emoji: "😐" },
};

export const IDENTITIES = [
  "行脚商人",
  "江湖侠客",
  "说书人",
  "游方郎中",
  "镖师",
];

// ── Map coordinates (800x500 canvas) ──

export const MAP_BOUNDS = { width: 800, height: 500 };

export const LOCATION_COORDS: Record<string, { x: number; y: number }> = {
  茶馆: { x: 200, y: 320 },
  集市: { x: 600, y: 320 },
  书院: { x: 200, y: 120 },
  河边: { x: 600, y: 120 },
};

// Location building sizes for the SVG map
export const LOCATION_BUILDINGS: Record<
  string,
  { x: number; y: number; w: number; h: number; label: string; emoji: string }
> = {
  茶馆: { x: 140, y: 270, w: 120, h: 90, label: "茶馆", emoji: "🍵" },
  集市: { x: 540, y: 270, w: 120, h: 90, label: "集市", emoji: "🏮" },
  书院: { x: 140, y: 70, w: 120, h: 90, label: "书院", emoji: "📚" },
  河边: { x: 540, y: 70, w: 120, h: 90, label: "河边", emoji: "🌿" },
};
