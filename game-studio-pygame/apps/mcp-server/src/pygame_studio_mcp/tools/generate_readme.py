"""Generate a README.md for a game project."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from pygame_studio_mcp.lib.paths import project_dir, templates_dir

_PROJECT_RE = re.compile(r"^[a-zA-Z0-9\-]+$")

GENRE_NAMES: dict[str, str] = {
    "flappy": "Flappy Bird (gravity dodge)",
    "shooter": "Shooter (top-down shooting)",
    "rogue": "Roguelike (dungeon exploration)",
    "fps": "FPS (raycasting)",
    "topdown": "Top-down action",
    "platformer": "Platformer (side-scrolling)",
}

GENRE_CONTROLS: dict[str, list[str]] = {
    "flappy": [
        "Space / Up arrow -- Flap",
        "R -- Restart",
        "Q / Esc -- Quit",
    ],
    "shooter": [
        "WASD / Arrow keys -- Move",
        "Space -- Shoot",
        "1/2/3 -- Difficulty select",
        "P -- Pause",
        "Q / Esc -- Quit",
    ],
    "rogue": [
        "WASD / Arrow keys -- Move",
        "Space -- Attack / Confirm",
        "1/2/3 -- Difficulty select",
        "P -- Pause",
        "Q / Esc -- Quit",
    ],
    "fps": [
        "W/S or Up/Down -- Forward/Back",
        "A/D or Left/Right -- Turn",
        "Space -- Shoot",
        "1/2/3 -- Difficulty select",
        "Q / Esc -- Quit",
    ],
    "topdown": [
        "WASD / Arrow keys -- Move",
        "Space -- Attack",
        "1/2/3 -- Difficulty select",
        "P -- Pause",
        "Q / Esc -- Quit",
    ],
    "platformer": [
        "A/D or Left/Right -- Move",
        "Space / W / Up -- Jump",
        "R -- Restart",
        "Q / Esc -- Quit",
    ],
}


def _difficulty_row(tier: str, params: dict[str, float]) -> str:
    parts: list[str] = []
    if "player_hp" in params:
        parts.append(f"HP {int(params['player_hp'])}")
    if "enemy_speed" in params:
        parts.append(f"Enemy speed {params['enemy_speed']}")
    if "enemy_count" in params:
        parts.append(f"Enemies {int(params['enemy_count'])}")
    if "enemy_hp" in params:
        parts.append(f"Enemy HP {int(params['enemy_hp'])}")
    if "gravity" in params:
        parts.append(f"Gravity {params['gravity']}")
    if "speed" in params:
        parts.append(f"Speed {params['speed']}")
    if "spawn_rate" in params:
        parts.append(f"Spawn rate {int(params['spawn_rate'])}")
    if "gap_size" in params:
        parts.append(f"Gap {int(params['gap_size'])}")
    return f"| {tier} | {'  '.join(parts)} |"


async def generate_readme(project: str) -> dict:
    """Generate README.md for a game project."""
    if not _PROJECT_RE.match(project):
        return {"success": False, "path": "", "content": "", "error": "Invalid project name"}

    dir_path = project_dir(project)
    config_path = dir_path / "config.yaml"

    config: dict = {}
    source = "generated-games"
    target_dir = dir_path

    if config_path.exists():
        try:
            raw = config_path.read_text(encoding="utf-8")
            config = yaml.safe_load(raw) or {}
        except Exception:
            pass
    else:
        tpl_config = templates_dir() / project / "config.yaml"
        if tpl_config.exists():
            try:
                raw = tpl_config.read_text(encoding="utf-8")
                config = yaml.safe_load(raw) or {}
                source = "templates"
                target_dir = templates_dir() / project
            except Exception:
                pass

    # List project files
    files: list[str] = []
    if target_dir.exists():
        files = sorted(
            f.name
            for f in target_dir.iterdir()
            if not f.name.startswith(".")
            and f.name != "__pycache__"
            and not f.name.endswith(".pyc")
        )

    name = str(config.get("name", project))
    genre = str(config.get("genre", "unknown"))
    genre_label = GENRE_NAMES.get(genre, genre)
    screen = config.get("screen", {})
    screen_w = screen.get("width", 800) if isinstance(screen, dict) else 800
    screen_h = screen.get("height", 600) if isinstance(screen, dict) else 600
    gameplay = config.get("gameplay", {})
    objective = str(gameplay.get("objective", "")) if isinstance(gameplay, dict) else ""
    duration = gameplay.get("duration", 0) if isinstance(gameplay, dict) else 0
    difficulty = config.get("difficulty", {})
    if not isinstance(difficulty, dict):
        difficulty = {}

    controls = GENRE_CONTROLS.get(genre, [
        "WASD / Arrow keys -- Move",
        "Space -- Action",
        "Q / Esc -- Quit",
    ])

    controls_md = "\n".join(
        f"- `{c.split(' -- ')[0]}` -- {c.split(' -- ')[1]}"
        for c in controls
    )

    difficulty_section = ""
    if difficulty:
        rows = "\n".join(
            _difficulty_row(tier, params)
            for tier, params in difficulty.items()
            if isinstance(params, dict)
        )
        if rows:
            difficulty_section = (
                "\n## Difficulty\n\n"
                "| Tier | Parameters |\n"
                "|------|------------|\n"
                f"{rows}\n"
            )

    py_files = [f for f in files if f.endswith(".py")]
    other_files = [f for f in files if not f.endswith(".py")]

    file_tree = "\n".join(f"|-- {f}" for f in py_files + other_files)

    readme = (
        f"# {name}\n\n"
        f"> {genre_label}\n\n"
        f"{'**Objective**: ' + objective + chr(10) if objective else ''}"
        f"**Session duration**: {duration}s\n\n"
        f"## Controls\n\n{controls_md}\n\n"
        f"- `R` / `Space` (Game Over) -- Restart\n"
        f"- `Q` / `Esc` -- Quit\n"
        f"{difficulty_section}\n"
        f"## Run\n\n"
        f"```bash\n"
        f"cd {source}/{project} && python3 main.py\n"
        f"```\n\n"
        f"## Display\n\n"
        f"- Resolution: {screen_w}x{screen_h}\n"
        f"- Requires: PyGame 2.5+\n\n"
        f"## Project structure\n\n"
        f"```\n"
        f"{project}/\n"
        f"{file_tree}\n"
        f"```\n\n"
        f"## Tech stack\n\n"
        f"- PyGame -- Graphics and input\n"
        f"- pygame-sdk -- Game engine (physics, collision, rendering, AI, scenes)\n"
        f"- Python 3.11+\n"
    )

    readme_path = target_dir / "README.md"
    try:
        readme_path.write_text(readme, encoding="utf-8")
    except Exception as exc:
        return {"success": False, "path": str(readme_path), "content": readme, "error": str(exc)}

    return {"success": True, "path": str(readme_path), "content": readme}
