"""Create a blank game project with standard Python file structure."""

from __future__ import annotations

from pathlib import Path

import yaml

from pygame_studio_mcp.lib.paths import project_dir


async def create_game(name: str, description: str) -> dict:
    """Create a new PyGame project with skeleton code."""
    dir_path = project_dir(name)
    dir_path.mkdir(parents=True, exist_ok=True)

    files: dict[str, str] = {
        "requirements.txt": (
            "pygame>=2.5.0\n"
            "pyyaml>=6.0\n"
        ),
        "main.py": (
            '"""Main entry point for the game."""\n'
            "\n"
            "import pygame\n"
            "import sys\n"
            "\n"
            "from config import load_config, default_config\n"
            "from model import GameModel\n"
            "\n"
            "\n"
            "def main():\n"
            "    config = load_config('config.yaml')\n"
            "    if config is None:\n"
            "        config = default_config()\n"
            "\n"
            "    pygame.init()\n"
            '    screen = pygame.display.set_mode(\n'
            '        (config["screen"]["width"], config["screen"]["height"])\n'
            "    )\n"
            f'    pygame.display.set_caption(config.get("name", "{name}"))\n'
            "\n"
            "    clock = pygame.time.Clock()\n"
            "    model = GameModel(config)\n"
            "\n"
            "    running = True\n"
            "    while running:\n"
            "        for event in pygame.event.get():\n"
            "            if event.type == pygame.QUIT:\n"
            "                running = False\n"
            "            model.handle_event(event)\n"
            "\n"
            "        model.update()\n"
            '        screen.fill((0, 0, 0))\n'
            "        model.draw(screen)\n"
            "        pygame.display.flip()\n"
            f'        clock.tick(config["screen"].get("fps", 60))\n'
            "\n"
            "    pygame.quit()\n"
            "    sys.exit(0)\n"
            "\n"
            "\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        ),
        "config.py": (
            '"""Configuration loader."""\n'
            "\n"
            "from typing import Any\n"
            "\n"
            "import yaml\n"
            "\n"
            "\n"
            "def load_config(path: str) -> dict[str, Any] | None:\n"
            '    """Load config from YAML file. Returns None on failure."""\n'
            "    try:\n"
            "        with open(path, 'r', encoding='utf-8') as f:\n"
            "            data = yaml.safe_load(f)\n"
            "        return data if isinstance(data, dict) else None\n"
            "    except (FileNotFoundError, yaml.YAMLError):\n"
            "        return None\n"
            "\n"
            "\n"
            "def default_config() -> dict[str, Any]:\n"
            '    """Return sensible defaults."""\n'
            "    return {\n"
            f'        "name": "{name}",\n'
            '        "screen": {"width": 800, "height": 600, "fps": 60},\n'
            "    }\n"
        ),
        "model.py": (
            '"""Game model: handles state, update, and draw."""\n'
            "\n"
            "from typing import Any\n"
            "\n"
            "import pygame\n"
            "\n"
            "\n"
            "class GameModel:\n"
            '    """Main game model."""\n'
            "\n"
            "    def __init__(self, config: dict[str, Any]):\n"
            "        self.config = config\n"
            '        self.running = True\n'
            "\n"
            "    def handle_event(self, event: pygame.event.Event) -> None:\n"
            '        """Handle a pygame event."""\n'
            "        pass\n"
            "\n"
            "    def update(self) -> None:\n"
            '        """Update game state per frame."""\n'
            "        pass\n"
            "\n"
            "    def draw(self, surface: pygame.Surface) -> None:\n"
            '        """Draw game to surface."""\n'
            "        pass\n"
        ),
        "config.yaml": yaml.safe_dump(
            {
                "name": name,
                "description": description,
                "genre": "shooter",
                "screen": {"width": 800, "height": 600, "fps": 60},
            },
            default_flow_style=False,
            allow_unicode=True,
        ),
    }

    files_created: list[str] = []
    for filename, content in files.items():
        (dir_path / filename).write_text(content, encoding="utf-8")
        files_created.append(filename)

    return {
        "success": True,
        "path": str(dir_path),
        "files_created": files_created,
    }
