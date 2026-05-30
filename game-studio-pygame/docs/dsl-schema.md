# Game DSL Schema (config.yaml)

All games are configured via `config.yaml`. This is the single source of truth for tuneable parameters.

## Schema

```yaml
# Required
name: string # Game name, lowercase hyphenated (e.g., "ninja-dodge")
genre: string # Template genre: flappy | shooter | platformer | rogue | fps | topdown

# Screen configuration
screen:
  width: int # Pixels, default 800
  height: int # Pixels, default 600
  fps: int # Target FPS, default 60

# Player configuration
player:
  color: [int, int, int] # RGB tuple, e.g., [255, 255, 0]
  hp: int # Hit points
  speed: float # Movement speed in pixels/frame
  size: [int, int] # Width, height in pixels

# Enemy configuration (genre-dependent)
enemy:
  color: [int, int, int] # RGB color
  speed: float # Movement speed
  spawn_rate: int # Frames between spawns
  hp: int # Hit points
  count: int # Initial count (rogue/topdown)

# Bullet/projectile configuration
bullet:
  color: [int, int, int] # RGB color
  speed: float # Pixels/frame
  size: [int, int] # Width, height

# Controls
controls:
  move: string # Movement type: none | arrows | wasd | mouse
  attack: string # Attack key: space | enter | click | auto

# Gameplay
gameplay:
  objective: string # score | survive | explore | reach_end
  duration: int # Max round duration in seconds, default 60

# World configuration (rogue/topdown)
world:
  width: int # World width in pixels
  height: int # World height in pixels
  tile_size: int # Tile size in pixels

# Enemy AI (shooter/rogue/topdown)
enemy_ai:
  behavior: string # idle | patrol | chase | flee | wander
  chase_range: float # Detection range in pixels
  attack_range: float # Attack range in pixels

# Difficulty tiers (required: easy, normal, hard)
difficulty:
  easy:
    gravity: float # Pixels/frame^2 (flappy, platformer)
    flap_impulse: float # Negative velocity (flappy)
    jump_impulse: float # Negative velocity (platformer)
    pipe_speed: float # Pixels/frame (flappy)
    pipe_gap: int # Pixels (flappy)
    enemy_speed: float # Pixels/frame (shooter, platformer)
    spawn_rate: int # Frames between spawns (shooter)
    spawn_interval: int # Frames between spawns (flappy)
    player_hp: int # Hit points
    grace_frames: int # Safe frames at start
  normal:
    # Same keys as easy, harder values
    ...
  hard:
    # Same keys as easy, hardest values
    ...
```

## Example: Flappy Game

```yaml
name: flappy-bird
genre: flappy
screen:
  width: 800
  height: 600
  fps: 60
player:
  color: [255, 255, 0]
  hp: 1
  size: [30, 24]
controls:
  move: none
  attack: space
gameplay:
  objective: score
  duration: 60
difficulty:
  easy:
    gravity: 0.3
    flap_impulse: -8
    pipe_speed: 2
    pipe_gap: 220
    spawn_interval: 90
    grace_frames: 120
  normal:
    gravity: 0.5
    flap_impulse: -10
    pipe_speed: 3
    pipe_gap: 180
    spawn_interval: 70
    grace_frames: 90
  hard:
    gravity: 0.7
    flap_impulse: -13
    pipe_speed: 5
    pipe_gap: 140
    spawn_interval: 50
    grace_frames: 60
```

## Example: Shooter Game

```yaml
name: zombie-survival
genre: shooter
screen:
  width: 800
  height: 600
  fps: 60
player:
  color: [0, 200, 0]
  hp: 4
  speed: 4
  size: [24, 24]
enemy:
  color: [200, 0, 0]
  speed: 2
  hp: 1
bullet:
  color: [255, 255, 100]
  speed: 6
  size: [4, 8]
controls:
  move: arrows
  attack: space
gameplay:
  objective: score
  duration: 60
difficulty:
  easy:
    enemy_speed: 1.5
    spawn_rate: 100
    player_hp: 6
    grace_frames: 120
  normal:
    enemy_speed: 3.0
    spawn_rate: 65
    player_hp: 4
    grace_frames: 90
  hard:
    enemy_speed: 4.5
    spawn_rate: 40
    player_hp: 2
    grace_frames: 60
```
