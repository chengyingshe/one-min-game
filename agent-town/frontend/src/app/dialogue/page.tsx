"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { NPC, DialogueMessage, Player, DialogueResponse } from "@/lib/types";
import { NPC_META, EMOTION_MAP } from "@/lib/constants";
import DialogueBubble from "@/components/DialogueBubble";
import RelationshipBar from "@/components/RelationshipBar";
import LoadingSpinner from "@/components/LoadingSpinner";

export const dynamic = "force-dynamic";

function DialogueContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const npcId = Number(searchParams.get("npc_id") || "1");
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [npc, setNpc] = useState<NPC | null>(null);
  const [player, setPlayer] = useState<Player | null>(null);
  const [messages, setMessages] = useState<DialogueMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function init() {
      try {
        const pid = localStorage.getItem("player_id");
        if (!pid) {
          router.push("/");
          return;
        }

        const [npcData, playerData, historyData] = await Promise.all([
          api.getNpc(npcId),
          api.getPlayer(Number(pid)),
          api.getHistory(npcId, Number(pid)),
        ]);
        setNpc(npcData);
        setPlayer(playerData);
        setMessages(historyData.history || []);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "加载失败";
        setError(msg);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [npcId, router]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || !npc || !player || sending) return;

    const content = input.trim();
    setInput("");
    setSending(true);

    setMessages((prev) => [
      ...prev,
      {
        speaker_type: "player",
        speaker_id: player.id,
        content,
        location: npc.current_location,
        day_number: 0,
      },
    ]);

    try {
      const resp: DialogueResponse = await api.sendDialogue(
        player.id,
        npc.id,
        content,
        npc.current_location,
      );
      setMessages((prev) => [
        ...prev,
        {
          speaker_type: "npc",
          speaker_id: npc.id,
          content: resp.reply,
          location: npc.current_location,
          day_number: 0,
        },
      ]);

      if (resp.affection_delta) {
        setPlayer((prev) => {
          if (!prev) return prev;
          const newRel = { ...prev.relationships };
          newRel[npc.id] = Math.max(
            0,
            Math.min(100, (newRel[npc.id] || 50) + resp.affection_delta),
          );
          return { ...prev, relationships: newRel };
        });
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "发送失败";
      setError(msg);
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner text="加载角色中..." />
      </div>
    );
  }

  if (!npc || !player) {
    return <div className="py-20 text-center text-red-500">角色未找到</div>;
  }

  const meta = NPC_META[npc.name] || { emoji: "👤", color: "gray" };
  const affection = player.relationships[npc.id] ?? 50;
  const emotion = EMOTION_MAP[npc.current_emotion] || {
    label: "平静",
    emoji: "😐",
  };

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-4 flex items-center justify-between">
        <button
          onClick={() => router.push("/town")}
          className="chinese-btn text-sm"
        >
          ← 返回小镇
        </button>
        <button
          onClick={() => router.push(`/trade?npc_id=${npc.id}`)}
          className="chinese-btn text-sm"
        >
          💰 交易
        </button>
      </div>

      <div className="chinese-card mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl">{npc.avatar_emoji || meta.emoji}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display text-lg">{npc.name}</span>
              <span className="rounded-full bg-amber-100 px-1.5 py-0.5 text-xs">
                {emotion.emoji} {emotion.label}
              </span>
            </div>
            <p className="text-xs text-stone-400">
              《{npc.source}》· {npc.occupation} · 📍 {npc.current_location}
            </p>
          </div>
        </div>
        <div className="mt-3">
          <RelationshipBar value={affection} />
        </div>
      </div>

      <div className="mb-4 h-[50vh] overflow-y-auto rounded-lg bg-white/50 border border-amber-200 p-4 space-y-3 scrollbar-thin">
        {messages.length === 0 && (
          <p className="py-8 text-center text-sm text-stone-400">
            你们初次见面，打个招呼吧...
          </p>
        )}
        {messages.map((msg, i) => (
          <DialogueBubble
            key={i}
            speakerType={msg.speaker_type}
            speakerName={npc.name}
            content={msg.content}
          />
        ))}
        {sending && <LoadingSpinner />}
        <div ref={chatEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="chinese-input flex-1"
          placeholder={`对${npc.name}说点什么...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={sending}
        />
        <button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="chinese-btn-primary"
        >
          发送
        </button>
      </div>

      {error && (
        <p className="mt-2 text-center text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}

export default function DialoguePage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DialogueContent />
    </Suspense>
  );
}
