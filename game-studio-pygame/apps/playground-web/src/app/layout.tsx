import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PyGame Playground",
  description: "Share and play 1-minute mini-games",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-gray-100 min-h-screen">
        <nav className="border-b border-gray-700 bg-gray-850">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="text-lg font-bold text-white">
              PyGame Playground
            </a>
            <div className="flex gap-4">
              <a href="/" className="text-sm text-gray-300 hover:text-white">
                Gallery
              </a>
              <a
                href="/upload"
                className="text-sm text-gray-300 hover:text-white"
              >
                Upload
              </a>
            </div>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
