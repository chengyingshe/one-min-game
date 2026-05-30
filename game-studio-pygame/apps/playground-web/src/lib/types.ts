export interface Game {
  id: number;
  name: string;
  display_name: string;
  description: string;
  genre: string;
  author_name: string;
  preview_image_url: string | null;
  screen_width: number;
  screen_height: number;
  controls: string;
  is_template: boolean;
  play_count: number;
  avg_rating: number;
  rating_count: number;
  created_at: string;
}

export interface RunResult {
  screenshots: string[];
  gif_url: string | null;
  exit_code: number;
  duration_ms: number;
}

export interface UploadPayload {
  name: string;
  display_name: string;
  description: string;
  genre: string;
  author_name: string;
  config_yaml: string;
  screen_width: number;
  screen_height: number;
  controls: string;
  file: File;
}

export const GENRES = [
  "arcade",
  "shooter",
  "platformer",
  "puzzle",
  "roguelike",
  "strategy",
  "racing",
  "other",
] as const;
export type Genre = (typeof GENRES)[number];
