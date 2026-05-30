"use client";

import { useState } from "react";
import { GENRES, type UploadPayload } from "@/lib/types";
import { uploadGame } from "@/lib/api";

export default function UploadForm() {
  const [form, setForm] = useState({
    name: "",
    display_name: "",
    description: "",
    genre: "arcade",
    author_name: "",
    config_yaml: "",
    screen_width: 800,
    screen_height: 600,
    controls: "",
  });
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const update = (field: string, value: string | number) =>
    setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!file) {
      setError("Please select a ZIP file.");
      return;
    }
    if (!form.name.match(/^[a-z0-9][a-z0-9_-]*$/)) {
      setError("Name must be lowercase alphanumeric with hyphens/underscores.");
      return;
    }

    setLoading(true);
    try {
      await uploadGame({ ...form, file });
      setSuccess(true);
      setForm({
        name: "",
        display_name: "",
        description: "",
        genre: "arcade",
        author_name: "",
        config_yaml: "",
        screen_width: 800,
        screen_height: 600,
        controls: "",
      });
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-xl space-y-4">
      {error && (
        <div className="p-3 rounded bg-red-900/50 text-red-300 text-sm">
          {error}
        </div>
      )}
      {success && (
        <div className="p-3 rounded bg-green-900/50 text-green-300 text-sm">
          Game uploaded successfully!
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="text-sm text-gray-300">Game Name (slug)</span>
          <input
            type="text"
            value={form.name}
            onChange={(e) => update("name", e.target.value)}
            className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
            placeholder="my-cool-game"
            required
          />
        </label>
        <label className="block">
          <span className="text-sm text-gray-300">Display Name</span>
          <input
            type="text"
            value={form.display_name}
            onChange={(e) => update("display_name", e.target.value)}
            className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
            placeholder="My Cool Game"
            required
          />
        </label>
      </div>

      <label className="block">
        <span className="text-sm text-gray-300">Description</span>
        <textarea
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
          rows={3}
        />
      </label>

      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="text-sm text-gray-300">Genre</span>
          <select
            value={form.genre}
            onChange={(e) => update("genre", e.target.value)}
            className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
          >
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-sm text-gray-300">Author</span>
          <input
            type="text"
            value={form.author_name}
            onChange={(e) => update("author_name", e.target.value)}
            className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
          />
        </label>
      </div>

      <label className="block">
        <span className="text-sm text-gray-300">Controls</span>
        <input
          type="text"
          value={form.controls}
          onChange={(e) => update("controls", e.target.value)}
          className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm focus:border-indigo-500 focus:outline-none"
          placeholder="Arrow keys to move, Space to shoot"
        />
      </label>

      <label className="block">
        <span className="text-sm text-gray-300">Game ZIP</span>
        <input
          type="file"
          accept=".zip"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mt-1 w-full text-sm text-gray-300 file:mr-3 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:bg-indigo-600 file:text-white hover:file:bg-indigo-500"
          required
        />
      </label>

      <label className="block">
        <span className="text-sm text-gray-300">config.yaml (optional)</span>
        <textarea
          value={form.config_yaml}
          onChange={(e) => update("config_yaml", e.target.value)}
          className="mt-1 w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 text-white text-sm font-mono focus:border-indigo-500 focus:outline-none"
          rows={5}
          placeholder="name: my-game&#10;genre: arcade&#10;screen:&#10;  width: 800&#10;  height: 600"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="px-6 py-2 rounded bg-indigo-600 text-white font-medium hover:bg-indigo-500 disabled:opacity-50"
      >
        {loading ? "Uploading..." : "Upload Game"}
      </button>
    </form>
  );
}
