# Contra Rush - Game Design Spec

## Overview

A 2D side-scrolling run-and-gun game inspired by Contra. Player controls a soldier who runs right through a TileMap level, jumps across platforms, and shoots enemies. Camera follows the player. Reach the end to win.

## Core Mechanic

**One verb: Shoot** — Move to navigate, shoot to kill, jump to survive.

## Controls

| Key                     | Action                             |
| ----------------------- | ---------------------------------- |
| Left/Right arrow or A/D | Move horizontally                  |
| Up arrow or W           | Jump                               |
| SPACE                   | Shoot in facing direction          |
| R                       | Restart (game over screen)         |
| 1/2/3                   | Select difficulty (menu/game over) |

Single-hand playable (left hand: WASD + SPACE, or right hand: arrows + SPACE).

## Visual Style

Colored rectangles on 800x600 pixel display. Tile size 32px.

| Element        | Color                     | Size  |
| -------------- | ------------------------- | ----- |
| Player         | Green (0, 200, 50)        | 24x32 |
| Enemy soldier  | Red (200, 50, 50)         | 24x32 |
| Turret         | Dark red (150, 30, 30)    | 24x24 |
| Flying drone   | Gray (150, 150, 150)      | 20x20 |
| Player bullet  | Yellow (255, 255, 0)      | 8x4   |
| Enemy bullet   | Orange (255, 150, 0)      | 8x4   |
| Health pickup  | Pink (255, 100, 150)      | 16x16 |
| Ground tiles   | Brown (100, 70, 40)       | 32x32 |
| Platform tiles | Gray-brown (120, 100, 80) | 32x32 |
| Sky background | Dark blue (20, 20, 50)    | —     |

## Level Design

### TileMap Structure

- 200 tiles wide x 19 tiles tall (6400x608 px)
- Loaded from string grid via `TileMap.load_from_strings()`
- Tile legend: `.` = empty, `#` = ground/solid, `=` = platform (one-way), `F` = finish zone

### Level Sections (left to right)

1. **Start zone** (cols 0-20): Flat ground, no enemies. Player learns controls.
2. **First engagement** (cols 20-50): Ground with 2-3 soldiers. Small gap.
3. **Platform section** (cols 50-90): Elevated platforms, soldiers, first turret.
4. **Gap gauntlet** (cols 90-130): Multiple gaps, flying drones, platforms.
5. **Turret alley** (cols 130-170): Ground level with turrets, soldiers behind cover.
6. **Final zone** (cols 170-200): Dense enemies, finish flag at col 195.

### Gravity and Jump Physics

- Gravity: 0.6 px/frame
- Jump impulse: -12 px/frame
- Player horizontal speed: 4-5 px/frame (varies by difficulty)

## Camera

SDK `Camera` in FOLLOW mode, tracking the player entity with lerp. Camera bounds clamped to level width so it doesn't show past the level edges.

## Entities

### Player

- Entity with EntityType.PLAYER
- 3-5 HP depending on difficulty
- Can shoot (cooldown ~15 frames)
- Faces left or right based on last movement direction
- Dies when HP reaches 0 or falls into a pit (y > screen height)

### Enemy Soldier

- Entity with EntityType.ENEMY
- Patrols left/right on its platform (or stands still)
- Shoots toward player every N frames (enemy_shoot_rate varies by difficulty)
- 1 HP, dies in one hit
- Score: +10 per kill

### Turret

- Entity with EntityType.ENEMY
- Stationary
- Fires bullets at regular intervals
- 2 HP
- Score: +25 per kill

### Flying Drone

- Entity with EntityType.ENEMY
- Moves in sine wave pattern (vertical oscillation while moving horizontally)
- 1 HP
- Score: +15 per kill

### Bullets

- Player bullets: travel in player's facing direction, destroy on hit or off-screen
- Enemy bullets: travel toward player's last known position, destroy on hit or off-screen

### Health Pickup

- Entity with EntityType.COLLECTIBLE
- Restores 1 HP on contact
- Placed at strategic locations in the level

## Game States

1. **MENU**: Title screen with difficulty selection. SPACE starts.
2. **GAMEPLAY**: Active gameplay with camera follow.
3. **GAME_OVER**: Death screen. Shows score and best. R or SPACE to restart.
4. **WIN**: Victory screen when reaching finish zone. Shows score and best.

## Difficulty Tiers

```yaml
easy:
  player_hp: 5
  player_speed: 5
  player_bullet_speed: 8
  enemy_speed: 1.5
  enemy_shoot_rate: 120
  grace_period: 180

normal:
  player_hp: 3
  player_speed: 4
  player_bullet_speed: 7
  enemy_speed: 2.5
  enemy_shoot_rate: 80
  grace_period: 120

hard:
  player_hp: 2
  player_speed: 4
  player_bullet_speed: 6
  enemy_speed: 3.5
  enemy_shoot_rate: 50
  grace_period: 60
```

## Scoring

| Action       | Points            |
| ------------ | ----------------- |
| Kill soldier | 10                |
| Kill turret  | 25                |
| Kill drone   | 15                |
| Reach finish | 100               |
| Health bonus | HP remaining x 20 |

## File Structure

```
generated-games/contra-rush/
  config.yaml       — All tuneable parameters
  config.py         — Config dataclass + load_config() + default_config()
  model.py          — ContraModel: level, entities, physics, collision
  view.py           — render() with camera offset
  main.py           — PyGame loop entry point
  requirements.txt  — pygame, pyyaml
```

## SDK Components Used

- `Entity`, `EntityStore`, `EntityType` — entity management
- `Camera` — follow camera with bounds
- `TileMap` — level terrain
- `SceneManager`, `SceneState` — game states
- `ScoreManager` — score tracking
- `Renderer` — all rendering
- `apply_gravity` — player jump physics
- `overlaps` (from collision) — AABB collision detection
- Color constants from `styles`

## Forbidden Patterns (per runtime-rules skill)

- No direct pygame.draw calls (use Renderer)
- No external assets
- No custom game loop (use standard PyGame loop)
- No I/O during gameplay
