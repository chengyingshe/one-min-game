# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered PyGame mini-game studio for the Vibe Hacks #04 hackathon (deadline 2026-05-30). Claude Code designs games via natural language, calls MCP tools to generate/build/run them, and the Playground web platform enables sharing and community voting.

**Competition context**: 100+ real users judge on-site. Games must be addictive ("再来一局"), 60-second sessions, single-hand playable.

## Build & Test Commands

```bash
# All commands run from game-studio-pygame/

# Full test suite
make test-all

# Individual test targets
make sdk-test                                    # PyGame SDK tests
make mcp-test                                    # MCP server tests
make template-test-flappy                        # Flappy template tests
make template-test-shooter                       # Shooter template tests
make template-test-platformer                    # Platformer template tests

# Install MCP server (editable)
make mcp-server                                  # pip install -e . in apps/mcp-server

# Build & run playground (Docker)
make playground-build                            # Build all Docker images
make playground-up                               # Start services (web :3080, api :8080)
make playground-down                             # Stop services

# Run a single game headless
cd generated-games/<game> && SDL_VIDEODRIVER=dummy python main.py

# Clean
make clean
```

## Architecture

Three-layer pipeline:

```
Claude Code (reasoning, design)
  → MCP Server (16 tools, Python)
    → PyGame SDK (25 modules, Python)
      → PyGame/SDL2 (graphics, input, audio)

Playground Platform:
  Next.js (:3080) → FastAPI (:8080) → Docker Runner → PyGame headless
```

### MCP Server (`apps/mcp-server/`)

Python package `pygame_studio_mcp`, entry point in `server.py`. Dispatches 21 tools:

- **Project lifecycle**: `create_project`, `create_game`, `scaffold_template`, `list_templates`
- **Code manipulation**: `write_game_file`, `read_game_file`, `apply_game_spec`
- **Build & run**: `build_game` (syntax check + requirements), `run_game` (headless), `validate_gameplay` (3s crash test)
- **Debugging**: `capture_frame` (stdout), `capture_screenshot` (PNG surface save), `list_sdk_api`
- **Tuning**: `tune_balance` (natural language → config.yaml adjustments), `check_environment`
- **Playground**: `upload_to_playground` (ZIP + upload), `list_playground_games`, `get_playground_game`, `download_from_playground`, `delete_playground_game`
- **Docs**: `generate_readme`

Playground integration tools use `PLAYGROUND_API_URL` env var (default `http://localhost:8080`). HTTP client is `httpx`.

Lib modules under `lib/`: `paths.py` (root resolution via `GAME_STUDIO_ROOT` env), `exec_utils.py` (subprocess with timeout), `dsl_parser.py` (GameSpec validation), `error_parser.py` (traceback parsing), `balance_tuner.py` (difficulty parameter mapping).

### PyGame SDK (`runtime/pygame-sdk/pygame_sdk/`)

25 modules re-exported from `__init__.py`. Games must use these, not raw pygame:

- **Entity system**: `entity.py` (Entity, EntityType, EntityStore), `collision.py` (AABB, resolution), `physics.py` (gravity, velocity), `force.py`, `material.py`
- **Rendering**: `renderer.py` (headless-capable, draw_entity/text/gameover, screenshot)
- **State**: `scene.py` (SceneManager: MENU/GAMEPLAY/PAUSED/GAME_OVER), `score.py` (ScoreManager), `config.py` (YAML loading), `difficulty.py`
- **Advanced**: `camera.py`, `raycast.py` (DDA pseudo-3D), `world.py` (TileMap), `dungeon.py` (procedural BSP), `pathfind.py` (A\*), `spatial.py` (SpatialHash), `patterns.py` (movement AI), `ai.py` (behavior states)
- **Utilities**: `vector.py` (Vector2D), `input.py`, `tick.py`, `styles.py`, `screenshot.py`

### Game Templates (`templates/`)

Three genres: `flappy/`, `shooter/`, `platformer/`. Each follows MVC with identical file structure:

- `config.yaml` — Game DSL with difficulty tiers (easy/normal/hard)
- `config.py` — `load_config()` and `default_config()`
- `model.py` — `GameModel` with `handle_event()`, `update()`, `draw()`
- `view.py` — `render()` using SDK Renderer
- `main.py` — PyGame loop entry point

### Playground (`apps/`)

- **playground-api/**: FastAPI + SQLAlchemy (SQLite). Routes: `/api/games` (CRUD + ratings), `/api/upload` (ZIP), `/api/runner` (Docker execution with screenshot/GIF capture), `/ws/play/{name}` (WebSocket interactive game streaming)
- **playground-web/**: Next.js 15 + React 19 + Tailwind CSS 4. Pages: gallery (`/`), upload (`/upload`), play (`/play/[name]` — interactive gameplay via WebSocket + canvas)

### Interactive Game Streaming

Browser plays games via WebSocket:

```
Browser (Canvas + keyboard) <--WS JSON--> FastAPI /ws/play/{name} <--subprocess--> game_stream_runner.py → PyGame headless
```

- `game_stream_runner.py`: Monkey-patches `Renderer.present()` to stream frames as base64 JPEG (~15KB/frame at ~15 FPS). Reads keyboard events from stdin JSON.
- `GamePlayer.tsx`: Canvas renderer + keyboard capture. States: idle → connecting → playing → gameover.
- Protocol: `ready` (canvas size), `frame` (base64 JPEG), `gameover`, `keydown`/`keyup` (input).

### Docker (`docker/`)

`game-runner/Dockerfile` — Python 3.11-slim with pygame/pyyaml/pillow. `run_game.py` sets `SDL_VIDEODRIVER=dummy`, monkey-patches `pygame.display.flip` for frame capture, generates GIF output.

`docker-compose.yml` — Three services: web (:3080), api (:8080), runner-build (one-time image build). Uses `game-data` volume for persistence.

## Game DSL (config.yaml)

All game parameters live in YAML. Valid genres: `flappy`, `shooter`, `rogue`, `fps`, `topdown`, `platformer`.

```yaml
name: zombie-survival
genre: shooter
screen: { width: 800, height: 600, fps: 60 }
player: { symbol: "@", hp: 5, color: [255, 255, 0] }
difficulty:
  easy: { enemy_speed: 1.5, spawn_rate: 90, player_hp: 6 }
  normal: { enemy_speed: 3.0, spawn_rate: 60, player_hp: 4 }
  hard: { enemy_speed: 4.5, spawn_rate: 40, player_hp: 2 }
```

## Skills (constraints for game generation)

Located in `skills/`. These guide Claude Code when generating games:

- **runtime-rules**: Must use SDK components (Renderer, Entity, Physics, SceneManager, ScoreManager). Forbidden: custom game loops, direct pygame draw calls, external assets, eval/exec/subprocess
- **game-design**: 60s sessions, ≤4 action keys, 800x600, instant restart, visible score, 2-3s grace period
- **game-balance**: Difficulty tiers with genre-specific parameter ranges. Auto-tuning maps feedback ("too hard/easy/fast/slow/boring/frustrating") to config adjustments
- **code-generation**: Build-fix loop (max 5 iterations). File order: config.yaml → config.py → model.py → view.py → main.py → requirements.txt

## MCP Server Configuration

`.mcp.json` configures the MCP server with `GAME_STUDIO_ROOT="."` (relative to project root). The server resolves paths via `lib/paths.py` using this env var, falling back to `__file__` parent traversal.

## Python Environment

- Python ≥3.11, venv at `.venv/`
- MCP server installed editable: `cd apps/mcp-server && pip install -e .`
- Main deps: pygame≥2.5.0, pyyaml≥6.0, mcp≥1.0.0, fastapi≥0.110.0, sqlalchemy≥2.0.0, pillow≥10.0.0, docker≥7.0.0
- Dev deps: pytest≥8.0.0, pytest-asyncio≥0.23.0
