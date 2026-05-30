"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { NPC, Player, TradeResult, Item } from "@/lib/types";
import { NPC_META } from "@/lib/constants";
import LoadingSpinner from "@/components/LoadingSpinner";

export const dynamic = "force-dynamic";

function TradeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const npcId = Number(searchParams.get("npc_id") || "1");

  const [npc, setNpc] = useState<NPC | null>(null);
  const [player, setPlayer] = useState<Player | null>(null);
  const [npcItems, setNpcItems] = useState<Item[]>([]);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [offeredGold, setOfferedGold] = useState(0);
  const [result, setResult] = useState<TradeResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [trading, setTrading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function init() {
      try {
        const pid = localStorage.getItem("player_id");
        if (!pid) {
          router.push("/");
          return;
        }

        const [npcData, playerData] = await Promise.all([
          api.getNpc(npcId),
          api.getPlayer(Number(pid)),
        ]);
        setNpc(npcData);
        setPlayer(playerData);

        const fakeItems: Record<number, Item[]> = {
          1: [
            {
              name: "《葬花吟》手稿",
              type: "collection",
              base_price: 80,
              description: "黛玉亲笔写就的诗稿",
            },
            {
              name: "玉佩",
              type: "collection",
              base_price: 120,
              description: "精致的美玉，黛玉自幼佩戴",
            },
          ],
          2: [
            {
              name: "如意金箍棒（仿）",
              type: "weapon",
              base_price: 200,
              description: "仿制版金箍棒",
            },
            {
              name: "花果山的桃子",
              type: "food",
              base_price: 15,
              description: "新鲜桃子，据说能延年益寿",
            },
          ],
          3: [
            {
              name: "丈八蛇矛",
              type: "weapon",
              base_price: 300,
              description: "张飞的成名兵器",
            },
            {
              name: "陈年佳酿",
              type: "food",
              base_price: 50,
              description: "上好的老酒，香气四溢",
            },
          ],
        };
        setNpcItems(fakeItems[npcId] || []);
      } catch (e: unknown) {
        setError((e as Error).message || "加载失败");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [npcId, router]);

  async function handleProposeTrade() {
    if (!selectedItem || !player || !npc) return;
    setTrading(true);
    setResult(null);
    try {
      const res = await api.proposeTrade({
        player_id: player.id,
        npc_id: npc.id,
        offered_item_name: "金币",
        offered_gold: offeredGold,
        npc_item_name: selectedItem.name,
        npc_item_price: selectedItem.base_price,
      });
      setResult(res);

      if (res.decision === "accept") {
        setPlayer((prev) =>
          prev
            ? { ...prev, wealth: prev.wealth - (res.fair_price || offeredGold) }
            : prev,
        );
      }
    } catch (e: unknown) {
      setError((e as Error).message || "交易失败");
    } finally {
      setTrading(false);
    }
  }

  if (loading)
    return (
      <div className="py-20 flex justify-center">
        <LoadingSpinner text="加载中..." />
      </div>
    );
  if (!npc || !player)
    return <div className="py-20 text-center text-red-500">角色未找到</div>;

  const meta = NPC_META[npc.name] || { emoji: "👤", color: "gray" };

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push(`/dialogue?npc_id=${npc.id}`)}
          className="chinese-btn text-sm"
        >
          ← 返回对话
        </button>
        <span className="text-sm text-stone-500">
          💰 你的金币:{" "}
          <span className="font-bold text-ink-black">{player.wealth}</span>
        </span>
      </div>

      <div className="chinese-card flex items-center gap-3">
        <span className="text-4xl">{npc.avatar_emoji || meta.emoji}</span>
        <div>
          <span className="font-display text-lg">{npc.name}</span>
          <p className="text-xs text-stone-400">
            好感度: {Math.round(player.relationships[npc.id] ?? 50)}
          </p>
        </div>
      </div>

      <h2 className="font-display text-lg">{npc.name} 的物品</h2>

      <div className="grid gap-3 sm:grid-cols-2">
        {npcItems.map((item) => (
          <button
            key={item.name}
            onClick={() => {
              setSelectedItem(item);
              setResult(null);
            }}
            className={`chinese-card text-left transition-all ${
              selectedItem?.name === item.name ? "ring-2 ring-amber-400" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-display text-sm">{item.name}</span>
              <span className="text-xs text-amber-600 font-bold">
                {item.base_price} 💰
              </span>
            </div>
            <p className="mt-1 text-xs text-stone-400">{item.description}</p>
          </button>
        ))}
      </div>

      {selectedItem && (
        <div className="chinese-card space-y-3">
          <h3 className="font-display">你的出价</h3>
          <div className="flex items-center gap-3">
            <label className="text-sm text-stone-600">金币数:</label>
            <input
              type="number"
              className="chinese-input w-32"
              value={offeredGold}
              onChange={(e) =>
                setOfferedGold(
                  Math.max(0, Math.min(player.wealth, Number(e.target.value))),
                )
              }
              min={0}
              max={player.wealth}
            />
            <button
              onClick={handleProposeTrade}
              disabled={trading || offeredGold <= 0}
              className="chinese-btn-primary"
            >
              {trading ? "谈判中..." : "💬 出价"}
            </button>
          </div>
        </div>
      )}

      {result && (
        <div
          className={`chinese-card ${result.decision === "accept" ? "border-green-400" : result.decision === "reject" ? "border-red-300" : ""}`}
        >
          <p className="mb-2 font-display">
            {result.decision === "accept"
              ? "✅ 交易成功"
              : result.decision === "counter"
                ? "🔄 讨价还价"
                : "❌ 拒绝交易"}
          </p>
          <p className="text-sm italic">&ldquo;{result.npc_reply}&rdquo;</p>
          <div className="mt-2 text-xs text-stone-400">
            合理价格: {result.fair_price} 金币
            {result.counter_offer && (
              <span> · 还价: {result.counter_offer} 金币</span>
            )}
          </div>
          {result.decision === "counter" && (
            <button
              onClick={async () => {
                setOfferedGold(result.counter_offer || result.fair_price);
                setResult(null);
              }}
              className="chinese-btn mt-2 text-sm"
            >
              接受还价
            </button>
          )}
        </div>
      )}

      {error && <p className="text-center text-sm text-red-500">{error}</p>}
    </div>
  );
}

export default function TradePage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <TradeContent />
    </Suspense>
  );
}
