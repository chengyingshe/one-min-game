import type { Game, RunResult, UploadPayload, Room } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

export async function listGames(params?: {
  genre?: string;
  search?: string;
  sort?: string;
  order?: string;
  limit?: number;
  offset?: number;
}): Promise<Game[]> {
  const sp = new URLSearchParams();
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) sp.set(k, String(v));
    }
  }
  return request(`/api/games?${sp.toString()}`);
}

export async function getGame(name: string): Promise<Game> {
  return request(`/api/games/${encodeURIComponent(name)}`);
}

export async function deleteGame(name: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/games/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`${res.status}`);
}

export async function rateGame(
  name: string,
  rating: number,
  sessionId: string,
): Promise<Game> {
  return request(`/api/games/${encodeURIComponent(name)}/rate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating, session_id: sessionId }),
  });
}

export async function incrementPlay(name: string): Promise<Game> {
  return request(`/api/games/${encodeURIComponent(name)}/play`, {
    method: "POST",
  });
}

export async function runGame(
  gameName: string,
  durationSeconds = 10,
  captureFrames = [30, 60, 90, 120],
): Promise<RunResult> {
  return request("/api/runner/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      game_name: gameName,
      duration_seconds: durationSeconds,
      capture_frames: captureFrames,
    }),
  });
}

export async function uploadGame(payload: UploadPayload): Promise<Game> {
  const form = new FormData();
  form.append("file", payload.file);
  form.append("name", payload.name);
  form.append("display_name", payload.display_name);
  form.append("description", payload.description);
  form.append("genre", payload.genre);
  form.append("author_name", payload.author_name);
  form.append("config_yaml", payload.config_yaml);
  form.append("screen_width", String(payload.screen_width));
  form.append("screen_height", String(payload.screen_height));
  form.append("controls", payload.controls);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

export function screenshotUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path.startsWith("/") ? path : "/" + path}`;
}

// WebSocket must connect directly to the API server (port 8080),
// not through Next.js rewrites which don't support WS proxying.
const WS_API_BASE = process.env.NEXT_PUBLIC_WS_API_URL || "";

function getWsBase(): string {
  if (WS_API_BASE) return WS_API_BASE.replace(/^http/, "ws");
  // Fallback: derive from current host, replacing port 3080→8080
  if (typeof window !== "undefined") {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname;
    return `${proto}//${host}:8080`;
  }
  return "ws://localhost:8080";
}

export function getWsPlayUrl(gameName: string): string {
  return `${getWsBase()}/ws/play/${encodeURIComponent(gameName)}`;
}

export async function createRoom(
  gameName: string,
  hostName: string,
  maxPlayers = 4,
): Promise<Room> {
  return request("/api/rooms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      game_name: gameName,
      host_name: hostName,
      max_players: maxPlayers,
    }),
  });
}

export async function getRoom(roomId: string): Promise<Room> {
  return request(`/api/rooms/${encodeURIComponent(roomId)}`);
}

export function getWsMultiplayerUrl(roomId: string): string {
  return `${getWsBase()}/ws/multiplayer/${encodeURIComponent(roomId)}`;
}

// Mystery game API
export async function createMysteryRoom(
  mode: string,
  hostName: string,
  maxPlayers = 4
): Promise<{ room_id: string; mode: string }> {
  return request("/api/mystery/rooms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mode,
      host_name: hostName,
      max_players: maxPlayers,
    }),
  });
}

export function getWsMysteryUrl(roomId: string): string {
  return `${getWsBase()}/ws/mystery/${encodeURIComponent(roomId)}`;
}
