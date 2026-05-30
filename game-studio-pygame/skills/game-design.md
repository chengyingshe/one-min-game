# Game Design Skill

This skill guides game design decisions for the PyGame Game Studio. It supports both template-based and open-ended game creation.

## Design Constraints

Every game must satisfy ALL of the following:

- **Short sessions (recommended ~1-2 minutes)**: Games are designed for quick rounds. Duration is flexible — there is no hard time limit. Most rounds should end due to player failure, not a timer.
- **Single-hand playable**: Maximum 4 action keys plus navigation keys (arrow/WASD). The player must be able to play using one hand on a standard keyboard.
- **One-sentence rules**: The complete rules must be explainable in a single sentence. Example: "Press SPACE to flap, avoid the pipes." The player must understand the rules within 5 seconds.
- **Colorful graphics**: Use PyGame surfaces with colored rectangles, shapes, and text. RGB color tuples for all visual elements. No external image files.
- **Screen resolution**: 800x600 pixels default. Games must render correctly at this resolution.
- **"One more try" loop**: The game over screen must immediately offer restart (SPACE or R). Best score must be visible. The restart must be near-instant with no loading screen.
- **Visible score**: The current score must always be visible during gameplay, typically in a status bar.
- **Difficulty tiers**: At minimum, easy/normal/hard tiers must be available, switchable from the menu and game-over screen via keys 1/2/3.
- **Grace period**: The first 2-3 seconds of gameplay must be safe. No damage, no death. Use a visible indicator during this period.

## Conversation Flow

When a user describes a game idea:

### Template Match

If the idea clearly maps to an existing template (flappy/shooter/platformer):

1. Tell the user it matches a template, offer template-based OR scratch generation.
2. If template: use `scaffold_template` + `apply_game_spec` to generate from the template.

### Novel or Hybrid Ideas

If the idea is novel, hybrid, or unclear:

1. Ask 2-3 clarifying questions:
   - What is the single core action? (one verb)
   - How does the player fail?
   - How does the player score?
2. After answers, generate from scratch.

### Simple Requests

Simple/clear requests (e.g., "make a flappy bird game") should generate directly without asking questions.

## Design Process

### 1. Identify Core Mechanic

Reduce the game to one verb:

- Flap, shoot, dodge, explore, catch, bounce, match, race, stack, jump, slice, dig, swing, spin, click

Only one core verb per game.

### 2. Map to SDK Building Blocks

Based on the core mechanic, select the appropriate SDK components:

- **Movement**: `apply_gravity` (falling), `apply_velocity` (direct), manual pos updates
- **Entities**: `EntityStore` for many objects, individual `Entity` for player
- **Collision**: `overlaps` for entity AABB, `hit_bounds`/`hit_ground` for boundaries, `check_collision_pairs` for many-vs-many
- **Rendering**: `Renderer` for all output, `draw_entity` for rectangles, `draw_text` for text overlays
- **Timing**: `TickScheduler` with `should_spawn` for periodic events
- **Input**: `InputMapper` for key bindings

### 3. Design Game State

Model class with standard fields:

- `config`, `scene`, `score`, `tick`, `player`, `entities`, `difficulty`, `frame`
- Plus game-specific state fields as needed

### 4. Define File Structure

Standard files (recommended):

- `main.py` -- Entry point. Creates model, runs PyGame loop.
- `model.py` -- Model class, constructor, reset().
- `config.py` -- Config dataclass, load_config(), default_config(), params().
- `config.yaml` -- YAML configuration with all tuneable parameters.
- `update.py` -- handle_event(), update() methods.
- `view.py` -- render() method using Renderer.
- `requirements.txt` -- Dependencies (pygame-sdk).

Optional game-specific files as needed (e.g., `entities.py`, `spawning.py`).

### 5. Progressive Difficulty

The game must get harder over time within a single round. Common approaches:

- Faster spawning
- Faster movement
- More enemies
- Narrower gaps
- Time-based scaling

## Templates as Reference

When generating from scratch, templates serve as reference for patterns. Call `list_templates` or read template source files to understand established patterns.

## Generation Workflow

1. Call `create_game` to set up project skeleton.
2. Call `list_sdk_api` to check available building blocks.
3. Call `write_game_file` for each source file.
4. Call `build_game` and enter build-fix loop (see code-generation skill).
5. Call `run_game` to test.
6. Call `validate_gameplay` to verify.

## Naming Conventions

- Game names: lowercase, hyphenated (e.g., `ninja-dodge`, `space-blaster`).
- Colors: RGB tuples (e.g., `(255, 255, 0)` for yellow).
- Difficulty keys: always `easy`, `normal`, `hard` (lowercase).
