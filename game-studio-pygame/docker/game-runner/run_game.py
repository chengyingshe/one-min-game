"""Headless game runner for capturing PyGame screenshots."""
from __future__ import annotations

import json
import os
import sys
import time
import importlib.util
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from PIL import Image


def load_game_module(game_dir: str):
    base = Path(game_dir)
    src_dir = base / "src"
    if not src_dir.exists():
        src_dir = base

    main_file = src_dir / "main.py"
    if not main_file.exists():
        py_files = list(src_dir.glob("*.py"))
        if py_files:
            main_file = py_files[0]
        else:
            raise FileNotFoundError(f"No Python files found in {src_dir}")

    spec = importlib.util.spec_from_file_location("__main__", main_file)
    module = importlib.util.module_from_spec(spec)
    return spec, module


def main():
    if len(sys.argv) < 2:
        print("Usage: run_game.py <json_config>", file=sys.stderr)
        sys.exit(1)

    config = json.loads(sys.argv[1])
    capture_frames = set(config.get("capture_frames", [30, 60, 90, 120]))
    duration_seconds = config.get("duration_seconds", 10)
    output_dir = Path(config.get("output_dir", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    game_dir = os.environ.get("GAME_DIR", "/game")

    # Screen size defaults (may be overridden by game)
    screen_width = 800
    screen_height = 600

    # Try reading config.yaml
    for candidate in [Path(game_dir) / "src" / "config.yaml", Path(game_dir) / "config.yaml"]:
        if candidate.exists():
            try:
                import yaml
                with open(candidate) as f:
                    game_config = yaml.safe_load(f)
                scr = game_config.get("screen", {})
                screen_width = scr.get("width", screen_width)
                screen_height = scr.get("height", screen_height)
            except Exception:
                pass
            break

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    # Monkey-patch pygame.display.flip to capture screenshots
    captured_files: list[str] = []
    frame_counter = [0]

    original_flip = pygame.display.flip

    def patched_flip():
        original_flip()
        fnum = frame_counter[0]
        if fnum in capture_frames:
            filename = f"frame_{fnum:05d}.png"
            filepath = str(output_dir / filename)
            data = pygame.image.tostring(screen, "RGB")
            img = Image.frombytes("RGB", (screen.get_width(), screen.get_height()), data)
            img.save(filepath)
            captured_files.append(filepath)
        frame_counter[0] += 1

    pygame.display.flip = patched_flip

    # Also patch pygame.event.get to auto-generate QUIT after duration
    deadline = time.time() + duration_seconds
    original_event_get = pygame.event.get

    def patched_event_get(*args, **kwargs):
        events = original_event_get(*args, **kwargs)
        if time.time() >= deadline:
            events = list(events)
            events.append(pygame.event.Event(pygame.QUIT))
        return events

    pygame.event.get = patched_event_get

    # Load and run the game
    start_time = time.time()
    try:
        spec, module = load_game_module(game_dir)
        # Set __name__ to __main__ so `if __name__ == "__main__": main()` triggers
        module.__name__ = "__main__"
        spec.loader.exec_module(module)
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 0
    except Exception as e:
        exit_code = 1
        print(f"Game error: {e}", file=sys.stderr)
    elapsed = time.time() - start_time

    pygame.quit()

    # Generate GIF
    gif_filename = None
    if len(captured_files) >= 2:
        gif_filename = "preview.gif"
        images = [Image.open(f) for f in captured_files]
        images[0].save(
            str(output_dir / gif_filename),
            save_all=True,
            append_images=images[1:],
            duration=400,
            loop=0,
        )

    # Write manifest
    capture_list = sorted(capture_frames)
    manifest = {
        "frames": [
            {"frame_number": capture_list[i] if i < len(capture_list) else i,
             "filename": Path(f).name}
            for i, f in enumerate(captured_files)
        ],
        "gif_url": gif_filename,
        "total_frames": frame_counter[0],
        "duration_seconds": elapsed,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
