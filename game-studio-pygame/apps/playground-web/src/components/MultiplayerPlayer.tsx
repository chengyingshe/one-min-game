"use client";

import { useEffect, useRef, useState, useCallback } from "react";

type GameState = "playing" | "gameover" | "error";

const GAME_KEYS = new Set([
  "ArrowUp",
  "ArrowDown",
  "ArrowLeft",
  "ArrowRight",
  " ",
  "Enter",
  "Escape",
  "w",
  "a",
  "s",
  "d",
  "z",
  "x",
  "c",
  "q",
  "e",
  "r",
  "b",
  "f",
  "Shift",
  "Control",
  "Tab",
  "Backspace",
]);

function keyToName(key: string): string {
  const map: Record<string, string> = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    " ": "space",
    Enter: "enter",
    Escape: "escape",
    Shift: "shift",
    Control: "ctrl",
    Tab: "tab",
    Backspace: "backspace",
  };
  return map[key] ?? key.toLowerCase();
}

interface PlayerInfo {
  id: string;
  name: string;
  color: number[];
}

interface Props {
  ws: WebSocket;
  playerId: string;
  playerColor: number[];
  players: PlayerInfo[];
  onQuit: () => void;
}

export default function MultiplayerPlayer({
  ws,
  playerId,
  playerColor,
  players,
  onQuit,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const wsRef = useRef<WebSocket>(ws);
  const [state, setState] = useState<GameState>("playing");
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
  const [errorMsg, setErrorMsg] = useState("");
  const [survivalTime, setSurvivalTime] = useState(0);

  useEffect(() => {
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "ready":
            setCanvasSize({ width: msg.width, height: msg.height });
            break;
          case "frame":
            drawFrame(msg.data);
            break;
          case "gameover":
            if (msg.survival_time) setSurvivalTime(msg.survival_time);
            if (msg.score) setSurvivalTime(msg.score);
            setState("gameover");
            break;
          case "error":
            setErrorMsg(msg.message || "Error");
            setState("error");
            break;
        }
      } catch {}
    };

    ws.onerror = () => {
      setErrorMsg("Connection lost");
      setState("error");
    };

    ws.onclose = () => {
      if (state === "playing") {
        setErrorMsg("Disconnected");
        setState("error");
      }
    };
  }, [ws, state]);

  const drawFrame = useCallback((b64data: string) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (!imgRef.current) imgRef.current = new Image();
    const img = imgRef.current;
    img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    img.src = "data:image/jpeg;base64," + b64data;
  }, []);

  // Keyboard input
  useEffect(() => {
    if (state !== "playing") return;

    const handleKey = (type: "keydown" | "keyup") => (e: KeyboardEvent) => {
      if (!GAME_KEYS.has(e.key)) return;
      e.preventDefault();
      e.stopPropagation();

      const w = wsRef.current;
      if (w && w.readyState === WebSocket.OPEN) {
        w.send(JSON.stringify({ type, key: keyToName(e.key) }));
      }
    };

    const onKeyDown = handleKey("keydown");
    const onKeyUp = handleKey("keyup");
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, [state]);

  return (
    <div className="space-y-3">
      <div className="relative bg-black rounded-lg overflow-hidden border border-gray-700">
        <canvas
          ref={canvasRef}
          width={canvasSize.width}
          height={canvasSize.height}
          className="w-full h-auto block"
          style={{ imageRendering: "pixelated", maxHeight: "70vh" }}
        />

        {/* Player indicator */}
        {state === "playing" && (
          <div className="absolute top-2 left-2 flex items-center gap-2 px-2 py-1 bg-black/60 rounded">
            <div
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor: `rgb(${playerColor.join(",")})`,
              }}
            />
            <span className="text-xs text-white">{playerId}</span>
          </div>
        )}

        {/* Overlay for non-playing states */}
        {state !== "playing" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
            {state === "gameover" && (
              <div className="text-center space-y-4">
                <p className="text-yellow-400 text-2xl font-bold">Game Over!</p>
                {survivalTime > 0 && (
                  <p className="text-gray-300">Survived: {survivalTime}s</p>
                )}
                <button
                  onClick={onQuit}
                  className="px-8 py-3 rounded-lg bg-indigo-600 text-white text-lg font-bold hover:bg-indigo-500"
                >
                  Back to Lobby
                </button>
              </div>
            )}
            {state === "error" && (
              <div className="text-center space-y-3">
                <p className="text-red-400 text-sm">{errorMsg}</p>
                <button
                  onClick={onQuit}
                  className="px-6 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-500"
                >
                  Back
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Players bar */}
      {state === "playing" && (
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-3">
            {players.map((p) => (
              <span key={p.id} className="flex items-center gap-1">
                <span
                  className="inline-block w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: `rgb(${p.color.join(",")})`,
                  }}
                />
                {p.name}
              </span>
            ))}
          </div>
          <button onClick={onQuit} className="text-red-400 hover:text-red-300">
            Quit
          </button>
        </div>
      )}
    </div>
  );
}
