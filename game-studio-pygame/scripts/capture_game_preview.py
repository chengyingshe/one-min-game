#!/usr/bin/env python3
"""Capture a preview screenshot from a PyGame game by running it headless.

Usage:
    python capture_game_preview.py <game_dir> [--output <path.png>] [--frame <N>]
    python capture_game_preview.py --all-templates [--output-dir <dir>]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
GENERATED_DIR = PROJECT_ROOT / "generated-games"


def detect_has_capture_support(game_dir: Path) -> bool:
    """Check if main.py supports CAPTURE_FRAME / CAPTURE_PATH env vars."""
    main_py = game_dir / "main.py"
    if not main_py.exists():
        return False
    content = main_py.read_text(encoding="utf-8")
    return "CAPTURE_FRAME" in content and "CAPTURE_PATH" in content


def capture_template(game_dir: Path, output_path: Path, frame: int = 90) -> bool:
    """Capture using built-in CAPTURE_FRAME / CAPTURE_PATH env var support.

    The game won't auto-quit in headless mode, so we kill it after a timeout.
    The screenshot is saved at the target frame (~1.5s for frame 90 at 60 FPS).
    """
    main_py = game_dir / "main.py"
    sdk_path = str((PROJECT_ROOT / "runtime" / "pygame-sdk").resolve())
    env = {
        **os.environ,
        "SDL_VIDEODRIVER": "dummy",
        "CAPTURE_FRAME": str(frame),
        "CAPTURE_PATH": str(output_path.resolve()),
        "PYTHONPATH": sdk_path,
    }

    proc = subprocess.Popen(
        [sys.executable, str(main_py)],
        cwd=str(game_dir.resolve()),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    if proc.returncode and proc.returncode != 0 and proc.returncode != -15:
        stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        if stderr.strip():
            print(f"  Game exited with code {proc.returncode}: {stderr[:200]}")

    return output_path.exists() and output_path.stat().st_size > 0


def capture_with_wrapper(game_dir: Path, output_path: Path, frame: int = 90) -> bool:
    """Capture by injecting a monkey-patching wrapper script.

    Writes a temporary wrapper that patches pygame.display.flip to save
    a screenshot at the target frame, then runs it as a subprocess.
    """
    wrapper_code = f'''"""Auto-generated headless capture wrapper."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Ensure game directory is on path so imports like `from model import ...` work
_game_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _game_dir)

# Ensure SDK is on path
_sdk = os.path.join(_game_dir, "..", "..", "runtime", "pygame-sdk")
if os.path.isdir(_sdk):
    sys.path.insert(0, os.path.abspath(_sdk))

import pygame
import importlib.util

_TARGET_FRAME = {frame}
_OUTPUT_PATH = {str(output_path)!r}
_DURATION_SECS = 10

# Read config for screen size
_w, _h = 800, 600
for _cand in ["config.yaml", "src/config.yaml"]:
    _cp = os.path.join(os.path.dirname(__file__), _cand)
    if os.path.exists(_cp):
        try:
            import yaml
            _cfg = yaml.safe_load(open(_cp))
            _scr = _cfg.get("screen", {{}})
            _w = _scr.get("width", _w)
            _h = _scr.get("height", _h)
        except Exception:
            pass
        break

pygame.init()
screen = pygame.display.set_mode((_w, _h))

# Post SPACE key to start gameplay (games typically start in MENU scene)
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {{"key": pygame.K_SPACE}}))

_frame_counter = [0]
_original_flip = pygame.display.flip

def _patched_flip():
    _original_flip()
    fnum = _frame_counter[0]
    if fnum == _TARGET_FRAME:
        try:
            pygame.image.save(screen, _OUTPUT_PATH)
        except Exception:
            pass
    _frame_counter[0] += 1

pygame.display.flip = _patched_flip

# Patch Renderer.present() so it calls flip even in headless mode.
# Otherwise the monkey-patch on flip() never fires.
try:
    from pygame_sdk.renderer import Renderer
    _original_present = Renderer.present
    def _patched_present(self):
        if self.screen is not None:
            pygame.display.flip()
        if self.clock is not None:
            self.clock.tick(self.fps)
    Renderer.present = _patched_present
except ImportError:
    pass

# Auto-quit after duration
import time
_deadline = time.time() + _DURATION_SECS
_original_get = pygame.event.get

def _patched_get(*args, **kwargs):
    events = _original_get(*args, **kwargs)
    if time.time() >= _deadline:
        events = list(events)
        events.append(pygame.event.Event(pygame.QUIT))
    return events

pygame.event.get = _patched_get

# Load and run the game's main.py
_main = os.path.join(_game_dir, "main.py")
if not os.path.exists(_main):
    _py_files = list(__import__("pathlib").Path(_game_dir).glob("*.py"))
    if _py_files:
        _main = str(_py_files[0])

spec = importlib.util.spec_from_file_location("__main__", _main)
mod = importlib.util.module_from_spec(spec)
mod.__name__ = "__main__"
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
finally:
    pygame.quit()
'''

    wrapper_path = (game_dir / "_capture_wrapper.py").resolve()
    wrapper_path.write_text(wrapper_code, encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(wrapper_path)],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            print(f"  Game exited with code {result.returncode}: {stderr[:500]}")
        elif not output_path.exists():
            print(f"  No output file produced (stderr: {result.stderr.decode('utf-8', errors='replace')[:300]})")
        return output_path.exists() and output_path.stat().st_size > 0
    finally:
        if wrapper_path.exists():
            wrapper_path.unlink()


def capture_game(game_dir: Path, output_path: Path, frame: int = 90) -> bool:
    """Capture a preview screenshot from a game directory.

    Returns True if a valid PNG was saved to output_path.
    """
    main_py = game_dir / "main.py"
    if not main_py.exists():
        print(f"  No main.py found in {game_dir}, skipping")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Always use the wrapper approach: it posts SPACE to start gameplay
    # (games begin in MENU), patches flip() + Renderer.present() for headless
    # capture, and auto-quits after 10 seconds.
    has_builtin = detect_has_capture_support(game_dir)
    if has_builtin:
        print(f"  Using wrapper (game has built-in CAPTURE_FRAME, wrapper adds SPACE injection + auto-quit)")
    else:
        print(f"  Using wrapper (monkey-patch capture)")
    return capture_with_wrapper(game_dir, output_path, frame)


def main():
    parser = argparse.ArgumentParser(description="Capture game preview screenshots")
    parser.add_argument("game_dir", nargs="?", help="Path to game directory")
    parser.add_argument("--output", "-o", help="Output PNG path")
    parser.add_argument("--frame", "-f", type=int, default=90, help="Frame number to capture (default: 90)")
    parser.add_argument("--all-templates", action="store_true", help="Capture all templates")
    parser.add_argument("--all-generated", action="store_true", help="Capture all generated games with source")
    parser.add_argument("--output-dir", default="data/screenshots", help="Output directory for --all-* modes")
    args = parser.parse_args()

    games_to_capture: list[tuple[Path, Path]] = []

    if args.all_templates:
        for d in sorted(TEMPLATES_DIR.iterdir()):
            if d.is_dir() and (d / "main.py").exists():
                out = Path(args.output_dir) / d.name / "preview.png"
                games_to_capture.append((d, out))

    if args.all_generated:
        for d in sorted(GENERATED_DIR.iterdir()):
            if d.is_dir() and (d / "main.py").exists():
                out = Path(args.output_dir) / d.name / "preview.png"
                games_to_capture.append((d, out))

    if args.game_dir:
        game_dir = Path(args.game_dir).resolve()
        output = Path(args.output) if args.output else Path(args.output_dir) / game_dir.name / "preview.png"
        games_to_capture.append((game_dir, output))

    if not games_to_capture:
        parser.print_help()
        sys.exit(1)

    success = 0
    for game_dir, output_path in games_to_capture:
        print(f"Capturing {game_dir.name} -> {output_path}")
        try:
            ok = capture_game(game_dir, output_path, frame=args.frame)
            if ok:
                size_kb = output_path.stat().st_size / 1024
                print(f"  OK ({size_kb:.1f} KB)")
                success += 1
            else:
                print(f"  FAILED (no output or empty file)")
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT")
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{success}/{len(games_to_capture)} captured successfully")
    sys.exit(0 if success == len(games_to_capture) else 1)


if __name__ == "__main__":
    main()
