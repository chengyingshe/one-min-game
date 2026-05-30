import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "时空杂货镇 - Agent Town",
  description: "AI Agent 社交模拟游戏 — 与经典文学人物在古风小镇相遇",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-parchment text-ink-black antialiased">
        <header className="border-b border-amber-300/50 bg-amber-50/60 px-4 py-3">
          <div className="mx-auto flex max-w-4xl items-center justify-between">
            <a
              href="/"
              className="font-display text-xl tracking-wider text-ink-black"
            >
              🏮 时空杂货镇
            </a>
            <nav className="flex gap-4 text-sm">
              <a
                href="/town"
                className="hover:text-chinese-red transition-colors"
              >
                小镇地图
              </a>
              <a
                href="/memories"
                className="hover:text-chinese-red transition-colors"
              >
                记忆回溯
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
