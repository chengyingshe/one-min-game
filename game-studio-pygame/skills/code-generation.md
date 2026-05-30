# Code Generation Skill

This skill defines the code generation process, patterns, and error resolution for PyGame Game Studio games.

## Build-Fix Loop

1. Call `build_game` with project name.
2. If success -- proceed to `run_game`.
3. If failure -- read `parsed_errors` from result.
4. For each error: `read_game_file` the file, analyze, fix, `write_game_file` corrected version.
5. Go back to step 1 (max 5 iterations).
6. If still failing after 5 attempts, show errors to user.

## File Generation Order

Generate files in this order to ensure dependencies are satisfied:

1. `config.yaml` -- all parameters defined first.
2. `config.py` -- Config dataclass matching YAML.
3. `model.py` -- Model class, constructor, reset().
4. `update.py` -- handle_event(), update() methods.
5. `view.py` -- render() method using Renderer.
6. `main.py` -- entry point with game loop.
7. `requirements.txt` -- dependencies.

## Common Patterns

### Model Constructor

```python
class GameModel:
    def __init__(self):
        self.config = load_config("config.yaml") or default_config()
        self.player = Entity(
            entity_type=EntityType.PLAYER,
            pos=Vector2D(self.config.screen.width // 2, self.config.screen.height // 2),
            size=Vector2D(32, 32),
            color=(255, 255, 0),
            hp=self.params().get("player_hp", 3),
        )
        self.entities = EntityStore()
        self.score = ScoreManager()
        self.scene = SceneManager()
        self.tick = TickScheduler(16)
        self.difficulty = "normal"
        self.frame = 0
        self.renderer = None

    def params(self):
        return self.config.difficulty.get(self.difficulty, self.config.difficulty.get("normal", {}))

    def reset(self):
        self.score.reset()
        self.scene.transition(SceneState.GAMEPLAY)
        self.tick.reset()
        self.frame = 0
        self.entities.clear()
```

### Event Handling Pattern

```python
def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
        if self.scene.is_(SceneState.MENU):
            if event.key == pygame.K_SPACE:
                self.scene.transition(SceneState.GAMEPLAY)
            elif event.key == pygame.K_1:
                self.difficulty = "easy"
            elif event.key == pygame.K_2:
                self.difficulty = "normal"
            elif event.key == pygame.K_3:
                self.difficulty = "hard"
        elif self.scene.is_(SceneState.GAMEOVER):
            if event.key in (pygame.K_SPACE, pygame.K_r):
                self.reset()
```

### Update Pattern

```python
def update(self):
    if not self.scene.is_playing():
        return

    self.frame += 1
    params = self.params()
    grace_frames = params.get("grace_frames", 60)

    # Apply physics
    apply_gravity(self.player, params.get("gravity", 0.5))
    clamp_position(self.player, 0, 0,
                   self.config.screen.width, self.config.screen.height)

    # Spawn enemies
    if self.tick.should_spawn(params.get("spawn_interval", 60)):
        self.spawn_enemy()

    # Check collisions (only after grace period)
    if self.frame > grace_frames:
        self.check_collisions()

    # Update entities
    for entity in self.entities.get_active():
        apply_velocity(entity)
```

### Render Pattern

```python
def render(self, renderer):
    renderer.clear()

    if self.scene.is_(SceneState.MENU):
        renderer.draw_text(self.config.name, 400, 200, TITLE_COLOR)
        renderer.draw_text("Press SPACE to start", 400, 300, HINT_COLOR)
        return

    if self.scene.is_(SceneState.GAMEOVER):
        renderer.draw_text("GAME OVER", 400, 200, GAMEOVER_COLOR)
        renderer.draw_text(f"Score: {self.score.current}", 400, 250, SCORE_COLOR)
        renderer.draw_text(f"Best: {self.score.best}", 400, 280, SCORE_COLOR)
        return

    # Gameplay rendering
    renderer.draw_entity(self.player)
    for entity in self.entities.get_active():
        renderer.draw_entity(entity)
    renderer.draw_text(f"Score: {self.score.current}", 10, 10, SCORE_COLOR)

    # Grace period indicator
    if self.frame < self.params().get("grace_frames", 60):
        renderer.draw_text("SAFE!", 400, 30, GRACE_COLOR)
```

## Error Categories and Fixes

| Error Pattern                               | Cause                    | Fix                                                 |
| ------------------------------------------- | ------------------------ | --------------------------------------------------- |
| `ImportError: No module named 'pygame_sdk'` | SDK path not in sys.path | Add `sys.path.insert(0, ...)` in main.py            |
| `ModuleNotFoundError`                       | Missing dependency       | Add to requirements.txt, run `pip install`          |
| `SyntaxError`                               | Invalid Python syntax    | Fix indentation, quotes, colons                     |
| `IndentationError`                          | Wrong indentation level  | Align with surrounding code                         |
| `NameError: name 'X' is not defined`        | Missing import or typo   | Import from pygame_sdk, check spelling              |
| `TypeError`                                 | Wrong argument types     | Check function signature via `list_sdk_api`         |
| `AttributeError`                            | Wrong attribute access   | Check Entity/Renderer API via `list_sdk_api`        |
| `KeyError`                                  | Missing config key       | Add key to config.yaml or use `.get()` with default |
| `IndexError`                                | Out of bounds            | Check list/EntityStore bounds before access         |
| `pygame.error`                              | PyGame not initialized   | Call `renderer.init()` before use                   |

## Using the SDK

Before generating code, call `list_sdk_api` once to verify available types and functions. When uncertain about an API, read a template file for reference patterns.

## Screenshot Capture

For headless mode (Docker/Playground), the game must support screenshot capture:

```python
import os

# In the game loop, check for capture environment variables
capture_frame = int(os.environ.get("CAPTURE_FRAME", "0"))
capture_path = os.environ.get("CAPTURE_PATH", "")

if capture_frame > 0 and self.frame == capture_frame and capture_path:
    pygame.image.save(self.renderer.screen, capture_path)
```
