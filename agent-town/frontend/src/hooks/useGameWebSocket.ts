"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { NpcPosition, NpcConversation, WsTickMessage } from "@/lib/types";

interface UseGameWebSocketReturn {
  positions: NpcPosition[];
  conversations: NpcConversation[];
  currentDay: number;
  currentTime: string;
  paused: boolean;
  connected: boolean;
  sendMessage: (msg: Record<string, unknown>) => void;
}

export function useGameWebSocket(): UseGameWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [positions, setPositions] = useState<NpcPosition[]>([]);
  const [conversations, setConversations] = useState<NpcConversation[]>([]);
  const [currentDay, setCurrentDay] = useState(1);
  const [currentTime, setCurrentTime] = useState("08:00");
  const [paused, setPaused] = useState(false);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/game`);

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      const data: WsTickMessage = JSON.parse(event.data);

      if (data.type === "init") {
        if (data.positions) setPositions(data.positions);
        if (data.current_day) setCurrentDay(data.current_day);
        if (data.current_time) setCurrentTime(data.current_time);
      }

      if (data.type === "tick") {
        if (data.positions) setPositions(data.positions);
        if (data.dialogues && data.dialogues.length > 0) {
          setConversations((prev) =>
            [...data.dialogues!, ...prev].slice(0, 50),
          );
        }
      }

      if (data.type === "status") {
        if (data.paused !== undefined) setPaused(data.paused);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Reconnect after 3 seconds
      setTimeout(() => connect(), 3000);
    };

    ws.onerror = () => ws.close();

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((msg: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return {
    positions,
    conversations,
    currentDay,
    currentTime,
    paused,
    connected,
    sendMessage,
  };
}
