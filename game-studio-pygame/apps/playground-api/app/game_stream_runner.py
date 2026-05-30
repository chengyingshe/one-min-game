"""Interactive game stream runner for browser-based gameplay.

Streams frames as base64 JPEG via stdout (line-delimited JSON).
Reads keyboard events from stdin (JSON lines).

Protocol:
  stdout → {"type": "ready", "width": W, "height": H}
  stdout → {"type": "frame", "data": "<base64_jpg>"}
  stdout → {"type": "gameover"}
  stdout → {"type": "error", "message": "..."}

  stdin  ← {"type": "keydown", "key": "space"}
  stdin  ← {"type": "keyup", "key": "space"}
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import threading
import time
import importlib.util
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from PIL import Image

# Key name → pygame key constant mapping
KEY_MAP = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "space": pygame.K_SPACE,
    "enter": pygame.K_RETURN,
    "escape": pygame.K_ESCAPE,
    "w": pygame.K_w,
    "a": pygame.K_a,
    "s": pygame.K_s,
    "d": pygame.K_d,
    "z": pygame.K_z,
    "x": pygame.K_x,
    "c": pygame.K_c,
    "q": pygame.K_q,
    "e": pygame.K_e,
    "r": pygame.K_r,
    "shift": pygame.K_LSHIFT,
    "ctrl": pygame.K_LCTRL,
    "tab": pygame.K_TAB,
    "backspace": pygame.K_BACKSPACE,
}

# Target ~15 FPS for streaming (capture every N-th frame at 60 FPS game rate)
FRAME_SKIP = 4

# Max session duration
MAX_DURATION = 90


def send_msg(msg: dict) -> None:
    """Write a JSON message to stdout (flushed immediately)."""
    sys.stdout.write(json.dumps(msg, separators=(",", ":")) + "\n")
    sys.stdout.flush()


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
        send_msg({"type": "error", "message": "Usage: game_stream_runner.py <game_dir>"})
        sys.exit(1)

    game_dir = sys.argv[1]
    if not Path(game_dir).exists():
        send_msg({"type": "error", "message": f"Game directory not found: {game_dir}"})
        sys.exit(1)

    # Read screen size from config.yaml
    screen_width, screen_height = 800, 600
    for candidate in [Path(game_dir) / "config.yaml", Path(game_dir) / "src" / "config.yaml"]:
        if candidate.exists():
            try:
                import yaml
                with open(candidate) as f:
                    cfg = yaml.safe_load(f) or {}
                scr = cfg.get("screen", {}) or {}
                screen_width = scr.get("width", screen_width)
                screen_height = scr.get("height", screen_height)
            except Exception:
                pass
            break

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Set up sys.path: game dir + SDK so Renderer patch can import pygame_sdk
    runner_parent = str(Path(__file__).resolve().parent)
    sys.path = [p for p in sys.path if p != runner_parent]
    game_src = str(Path(game_dir).resolve())
    if game_src not in sys.path:
        sys.path.insert(0, game_src)
    for sdk_candidate in [Path("/sdk"), Path(__file__).resolve().parent.parent.parent.parent / "runtime" / "pygame-sdk"]:
        sdk_str = str(sdk_candidate)
        if sdk_candidate.exists() and sdk_str not in sys.path:
            sys.path.insert(0, sdk_str)
            break

    # Input queue: populated by stdin reader thread, consumed by patched event.get
    input_events: list[pygame.event.Event] = []
    input_lock = threading.Lock()

    # Key state dict: tracks held keys for pygame.key.get_pressed replacement.
    # Pygame key constants like K_LEFT (1073741904) are ~1B, so use dict not list.
    from collections import defaultdict
    key_state: defaultdict[int, int] = defaultdict(int)

    # Multiplayer support
    multiplayer_mode = [False]
    player_key_states: dict[str, dict[int, int]] = {}

    def stdin_reader():
        """Read keyboard events from stdin in a background thread."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            # Multiplayer: start_game message — create per-player key state entries
            if msg_type == "start_game" and not multiplayer_mode[0]:
                multiplayer_mode[0] = True
                for p in msg.get("players", []):
                    pid = p.get("id", "")
                    if pid and pid not in player_key_states:
                        player_key_states[pid] = defaultdict(int)
                continue

            # Multiplayer: player_left
            if msg_type == "player_left":
                pid = msg.get("player_id", "")
                if pid in player_key_states:
                    del player_key_states[pid]
                continue

            # Check for player-tagged input
            player_tag = msg.get("player")
            key_name = msg.get("key", "")

            pygame_key = KEY_MAP.get(key_name)
            if pygame_key is not None:
                if multiplayer_mode[0] and player_tag:
                    # Multiplayer: per-player key state
                    if player_tag not in player_key_states:
                        player_key_states[player_tag] = defaultdict(int)
                    if msg_type == "keydown":
                        player_key_states[player_tag][pygame_key] = 1
                    elif msg_type == "keyup":
                        player_key_states[player_tag][pygame_key] = 0
                else:
                    # Single-player (legacy)
                    if msg_type == "keydown":
                        key_state[pygame_key] = 1
                        with input_lock:
                            input_events.append(
                                pygame.event.Event(pygame.KEYDOWN, key=pygame_key, mod=0)
                            )
                    elif msg_type == "keyup":
                        key_state[pygame_key] = 0
                        with input_lock:
                            input_events.append(
                                pygame.event.Event(pygame.KEYUP, key=pygame_key, mod=0)
                            )

    reader_thread = threading.Thread(target=stdin_reader, daemon=True)
    reader_thread.start()

    # Monkey-patch pygame.event.get to inject keyboard events from stdin
    original_event_get = pygame.event.get
    game_over_sent = [False]

    def patched_event_get(*args, **kwargs):
        events = list(original_event_get(*args, **kwargs))
        with input_lock:
            events.extend(input_events)
            input_events.clear()
        return events

    pygame.event.get = patched_event_get

    # Monkey-patch pygame.key.get_pressed to return tracked key state.
    # Under SDL_VIDEODRIVER=dummy, SDL never receives keyboard events, so
    # the real get_pressed() always returns all zeros. We replace it with
    # our key_state array updated by the stdin reader.
    original_get_pressed = pygame.key.get_pressed

    def patched_get_pressed():
        return key_state.copy()  # return a copy so callers can't mutate our state

    pygame.key.get_pressed = patched_get_pressed

    # Monkey-patch pygame.display.flip to stream frames
    original_flip = pygame.display.flip
    frame_counter = [0]
    start_time = time.time()

    def patched_flip():
        original_flip()

        elapsed = time.time() - start_time
        if elapsed > MAX_DURATION:
            if not game_over_sent[0]:
                game_over_sent[0] = True
                send_msg({"type": "gameover"})
            return

        fnum = frame_counter[0]
        frame_counter[0] += 1

        # Skip frames to target ~15 FPS
        if fnum % FRAME_SKIP != 0:
            return

        try:
            # Use get_surface() instead of closure-captured screen,
            # because the game may call pygame.display.set_mode() again.
            current_screen = pygame.display.get_surface()
            if current_screen is None:
                return
            data = pygame.image.tostring(current_screen, "RGB")
            img = Image.frombytes("RGB", (current_screen.get_width(), current_screen.get_height()), data)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            send_msg({"type": "frame", "data": b64})
        except Exception:
            pass

    pygame.display.flip = patched_flip

    # Also patch Renderer.present to always call flip even in headless mode
    try:
        from pygame_sdk.renderer import Renderer
        _original_present = Renderer.present

        def patched_present(self_renderer):
            # Force flip even in headless mode
            if self_renderer.screen is not None:
                pygame.display.flip()
            if self_renderer.clock is not None:
                self_renderer.clock.tick(self_renderer.fps)

        Renderer.present = patched_present
    except ImportError:
        pass

    # Signal ready
    send_msg({"type": "ready", "width": screen_width, "height": screen_height})

    # Load and run the game
    try:
        spec, module = load_game_module(game_dir)
        module.__name__ = "__main__"

        # Always inject multiplayer state (mutable references — updated by stdin reader thread)
        module.multiplayer_mode = multiplayer_mode
        module.player_key_states = player_key_states

        # Also set on __main__ module so game code using sys.modules["__main__"] finds them.
        # Without this, model.py's _detect_multiplayer() gets None because player_key_states
        # is a local in main(), not a module attribute of the stream runner.
        _main_mod = sys.modules.get("__main__")
        if _main_mod is not None:
            _main_mod.player_key_states = player_key_states
            _main_mod.multiplayer_mode = multiplayer_mode

        spec.loader.exec_module(module)
    except SystemExit:
        pass
    except Exception as e:
        if not game_over_sent[0]:
            send_msg({"type": "error", "message": str(e)[:500]})
    finally:
        if not game_over_sent[0]:
            send_msg({"type": "gameover"})
        pygame.quit()


if __name__ == "__main__":
    main()
