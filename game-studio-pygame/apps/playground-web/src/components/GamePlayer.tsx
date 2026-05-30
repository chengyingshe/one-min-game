"use client";

import { useEffect, useRef, useState, useCallback } from "react";

type GameState = "idle" | "connecting" | "playing" | "gameover" | "error";

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

interface Props {
  gameName: string;
  wsUrl: string;
  controls?: string;
}

export default function GamePlayer({ gameName, wsUrl, controls }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [state, setState] = useState<GameState>("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  const drawFrame = useCallback((b64data: string) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (!imgRef.current) {
      imgRef.current = new Image();
    }
    const img = imgRef.current;
    img.onload = () => {
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = "data:image/jpeg;base64," + b64data;
  }, []);

  const startGame = useCallback(() => {
    setState("connecting");
    setErrorMsg("");

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      // Will transition to "playing" on first "ready" message
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        switch (msg.type) {
          case "ready":
            setCanvasSize({ width: msg.width, height: msg.height });
            setState("playing");
            break;
          case "frame":
            drawFrame(msg.data);
            break;
          case "gameover":
            setState("gameover");
            break;
          case "error":
            setErrorMsg(msg.message || "Unknown error");
            setState("error");
            break;
        }
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onerror = () => {
      setErrorMsg("Connection failed");
      setState("error");
    };

    ws.onclose = () => {
      if (state === "playing" || state === "connecting") {
        setState("idle");
      }
      wsRef.current = null;
    };
  }, [wsUrl, drawFrame, state]);

  // Keyboard input handling
  useEffect(() => {
    if (state !== "playing") return;

    const handleKey = (type: "keydown" | "keyup") => (e: KeyboardEvent) => {
      if (!GAME_KEYS.has(e.key)) return;
      e.preventDefault();
      e.stopPropagation();

      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type, key: keyToName(e.key) }));
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

        {/* Overlay for non-playing states */}
        {state !== "playing" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
            {state === "idle" && (
              <div className="text-center space-y-4">
                <p className="text-gray-300 text-lg">Ready to play?</p>
                <button
                  onClick={startGame}
                  className="px-8 py-3 rounded-lg bg-green-600 text-white text-lg font-bold hover:bg-green-500 transition-colors"
                >
                  Start Game
                </button>
                {controls && (
                  <p className="text-xs text-gray-500 mt-2">
                    Controls: {controls}
                  </p>
                )}
              </div>
            )}
            {state === "connecting" && (
              <div className="text-center space-y-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-400 mx-auto" />
                <p className="text-gray-300">Connecting...</p>
              </div>
            )}
            {state === "gameover" && (
              <div className="text-center space-y-4">
                <p className="text-yellow-400 text-2xl font-bold">Game Over!</p>
                <button
                  onClick={startGame}
                  className="px-8 py-3 rounded-lg bg-green-600 text-white text-lg font-bold hover:bg-green-500 transition-colors"
                >
                  Play Again
                </button>
              </div>
            )}
            {state === "error" && (
              <div className="text-center space-y-3">
                <p className="text-red-400 text-sm">{errorMsg}</p>
                <button
                  onClick={startGame}
                  className="px-6 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-500"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Controls hint */}
      {state === "playing" && (
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Use keyboard to play — arrow keys, space, enter</span>
          <button
            onClick={() => {
              wsRef.current?.close();
              setState("idle");
            }}
            className="text-red-400 hover:text-red-300"
          >
            Quit Game
          </button>
        </div>
      )}
    </div>
  );
}
