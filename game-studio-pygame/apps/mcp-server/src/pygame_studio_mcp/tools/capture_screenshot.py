"""Capture a screenshot from a PyGame project using surface save."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.paths import project_dir


async def capture_screenshot_base64(project: str) -> str | None:
    """Run the game headless for one frame and return a base64-encoded PNG screenshot.

    Returns None if the capture fails.
    """
    dir_path = project_dir(project)
    main_py = dir_path / "main.py"

    if not main_py.exists():
        return None

    capture_script = dir_path / "_capture_frame.py"
    capture_script.write_text(
        '"""One-frame capture helper."""\n'
        "import os\n"
        "os.environ['SDL_VIDEODRIVER'] = 'dummy'\n"
        "import pygame\n"
        "import sys\n"
        "\n"
        "from config import load_config, default_config\n"
        "from model import GameModel\n"
        "\n"
        "config = load_config('config.yaml') or default_config()\n"
        "pygame.init()\n"
        "w = config.get('screen', {}).get('width', 800)\n"
        "h = config.get('screen', {}).get('height', 600)\n"
        "screen = pygame.display.set_mode((w, h))\n"
        "\n"
        "model = GameModel(config)\n"
        "model.update()\n"
        "\n"
        "# Try model.draw(screen) first; fall back to view.render(model, Renderer) for templates\n"
        "if hasattr(model, 'draw'):\n"
        "    model.draw(screen)\n"
        "else:\n"
        "    try:\n"
        "        from view import render\n"
        "        from pygame_sdk.renderer import Renderer\n"
        "        r = Renderer(w, h, config.get('screen', {}).get('fps', 60))\n"
        "        r.init_headless()\n"
        "        render(model, r)\n"
        "        r.present()\n"
        "    except Exception:\n"
        "        pass\n"
        "\n"
        "pygame.display.flip()\n"
        "pygame.image.save(screen, '_screenshot.png')\n"
        "pygame.quit()\n",
        encoding="utf-8",
    )

    try:
        result = run(
            ["python3", "_capture_frame.py"],
            cwd=str(dir_path),
            timeout=10,
        )

        screenshot_path = dir_path / "_screenshot.png"
        if not screenshot_path.exists():
            return None

        img_data = screenshot_path.read_bytes()
        return base64.b64encode(img_data).decode("ascii")
    except Exception:
        return None
    finally:
        for tmp in [capture_script, dir_path / "_screenshot.png"]:
            if tmp.exists():
                tmp.unlink()


async def capture_screenshot(project: str) -> dict:
    """Run the game briefly in headless mode and capture a screenshot.

    Uses SDL_VIDEODRIVER=dummy and a helper script that renders one frame
    and saves to a PNG file. Returns base64-encoded image data.
    """
    dir_path = project_dir(project)
    main_py = dir_path / "main.py"

    if not main_py.exists():
        return {"success": False, "error": "main.py not found"}

    base64_data = await capture_screenshot_base64(project)
    if base64_data is None:
        return {"success": False, "error": "Screenshot not generated"}

    import base64 as _b64
    img_data = _b64.b64decode(base64_data)
    return {
        "success": True,
        "image_base64": base64_data,
        "format": "png",
        "size_bytes": len(img_data),
    }
