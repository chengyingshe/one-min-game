# Architecture

## System Overview

```
Claude Code (reasoning, design, debug)
    → PyGame MCP Server (Python, 16 tools, stdio transport)
        → PyGame Runtime SDK (Python, 14+ modules)
            → PyGame / SDL2 (graphics, input, audio)

Playground Platform:
    Browser → Next.js (3000) → FastAPI (8000) → Docker Game Runner → PyGame headless
```

## Layers

### Layer 1: Claude Code

- Thinks and designs games from natural language
- Calls MCP tools to create, build, run, tune games
- Follows skills (game-design, runtime-rules, game-balance, code-generation)

### Layer 2: MCP Server (Python)

- 16 tools registered via `mcp` Python SDK
- stdio transport, registered in `.mcp.json`
- Tools: check_environment, create_project, list_templates, scaffold_template, apply_game_spec, create_game, write_game_file, read_game_file, build_game, run_game, validate_gameplay, capture_frame, capture_screenshot, tune_balance, list_sdk_api, generate_readme
- Shared lib: paths, exec_utils, dsl_parser, balance_tuner, error_parser

### Layer 3: PyGame Runtime SDK (Python)

- Core modules: entity, vector, physics, collision, renderer, scene, score, tick, input, config, difficulty, material, force
- Advanced modules: patterns, world, dungeon, pathfind, camera, raycast, spatial, ai
- Utility: styles, screenshot
- Games import via sys.path to local SDK directory

### Layer 4: Playground Platform

- **FastAPI backend**: CRUD API, Docker game runner orchestration, file upload
- **Next.js frontend**: Gallery, upload, game preview with screenshots
- **Docker runner**: Headless PyGame container, captures screenshots at specified frames
- **Database**: SQLite for game metadata
- **Storage**: Local filesystem for game source and screenshots

## Data Flow

### Game Creation

1. User describes game → Claude Code calls MCP tools
2. `create_game` → project skeleton (main.py, model.py, config.py, config.yaml, update.py, view.py)
3. `write_game_file` → writes each file using SDK imports
4. `build_game` → py_compile syntax check + pip install deps
5. `run_game` → python main.py (with or without display)
6. `capture_frame` → headless run, PyGame surface → PNG
7. `validate_gameplay` → 5s headless run, no crash = valid

### Playground Upload

1. User uploads game ZIP via web UI
2. FastAPI extracts to GAMES_DIR
3. Docker runner executes headlessly, captures screenshots
4. Frontend displays screenshot gallery + game metadata

## Deployment

Docker Compose on Tencent Cloud:

- `web` (Next.js:3000) - frontend
- `api` (FastAPI:8000) - backend + Docker socket access
- `runner-build` - builds pygame-runner image
- `game-data` volume - persistent storage
