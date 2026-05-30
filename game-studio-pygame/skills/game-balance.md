# Game Balance Skill

This skill defines the tuning parameters and heuristics for balancing PyGame games. Use it when creating a new game or adjusting an existing one via `tune_balance`.

## Core Principles

- **Achievable grace period**: A new player must survive 10-15 seconds on their first attempt on Normal difficulty. Grace period covers 2-3 seconds of safety, and first threats must be avoidable without practice.
- **Gradual linear ramp**: Difficulty increases linearly within a round. No sudden spikes.
- **Fair death**: The player must always see what killed them. No invisible damage, no off-screen kills.
- **Score accessibility**: A bad player should achieve roughly 10% of a good player's score.
- **Short rounds**: Games should aim for rounds that feel quick and replayable. Duration is flexible based on game design.

## Difficulty Tiers

Each game must define three tiers with consistent relationships:

### Easy

- 50% slower than Normal (gravity, speed, spawn rate).
- Generous hitboxes (larger gaps, wider collision forgiveness).
- Extra HP or lives (+1 or +2 over Normal).
- 0.5x score multiplier.
- Extended grace period (1.5x Normal grace frames).

### Normal

- Baseline. All balance testing targets Normal.
- 1.0x score multiplier.
- Standard grace period (2-3 seconds).

### Hard

- 50% faster than Normal.
- Strict hitboxes (smaller gaps, tighter collision).
- Reduced HP or lives (-1 or -2 from Normal, minimum 1).
- 2.0x score multiplier.
- Shortened grace period (0.6x Normal grace frames).

## Per-Genre Parameter Ranges

Values are in pixels and frames, adapted from the terminal version.

### Flappy

| Parameter      | Easy        | Normal     | Hard       | Unit         |
| -------------- | ----------- | ---------- | ---------- | ------------ |
| gravity        | 0.25 - 0.35 | 0.4 - 0.55 | 0.6 - 0.8  | pixels/frame |
| flap_impulse   | -7 to -9    | -9 to -12  | -12 to -15 | pixels/frame |
| pipe_speed     | 2 - 3       | 3 - 4      | 5 - 6      | pixels/frame |
| pipe_gap       | 200 - 240   | 160 - 200  | 120 - 160  | pixels       |
| spawn_interval | 80 - 100    | 60 - 80    | 45 - 60    | frames       |
| grace_frames   | 90 - 120    | 60 - 90    | 36 - 60    | frames       |

### Shooter

| Parameter    | Easy      | Normal    | Hard      | Unit                  |
| ------------ | --------- | --------- | --------- | --------------------- |
| enemy_speed  | 1.0 - 2.0 | 2.0 - 3.5 | 3.5 - 5.0 | pixels/frame          |
| spawn_rate   | 80 - 120  | 50 - 80   | 30 - 50   | frames between spawns |
| player_hp    | 5 - 7     | 3 - 5     | 2 - 3     | hits                  |
| bullet_speed | 5 - 8     | 4 - 6     | 3 - 5     | pixels/frame          |
| grace_frames | 90 - 120  | 60 - 90   | 36 - 60   | frames                |

### Platformer

| Parameter    | Easy       | Normal     | Hard       | Unit         |
| ------------ | ---------- | ---------- | ---------- | ------------ |
| gravity      | 0.3 - 0.5  | 0.5 - 0.8  | 0.8 - 1.2  | pixels/frame |
| player_speed | 3 - 5      | 4 - 6      | 5 - 8      | pixels/frame |
| jump_impulse | -10 to -12 | -12 to -14 | -14 to -17 | pixels/frame |
| platform_gap | 80 - 120   | 60 - 100   | 40 - 80    | pixels       |
| enemy_speed  | 0.5 - 1.5  | 1.5 - 3.0  | 3.0 - 4.5  | pixels/frame |
| grace_frames | 90 - 120   | 60 - 90    | 36 - 60    | frames       |

## Auto-Tuning Rules

When a user reports balance issues, apply these deterministic adjustments:

### "too hard"

For each tier:

- Reduce gravity (flappy/platformer) or enemy speed (shooter) by 15%.
- Increase gap (flappy/platformer) or player HP (shooter) by 1.
- Increase grace_frames by 30 (at 60fps).
- Increase spawn_interval by 10.

### "too easy"

For each tier:

- Increase gravity or enemy speed by 15%.
- Decrease gap or player HP by 1 (minimum 1).
- Decrease grace_frames by 30 (minimum 30).
- Decrease spawn_interval by 10 (minimum 20).

### "too fast"

- Increase spawn_interval by 20% (round to nearest integer).
- Reduce speed by 10%.
- Increase grace_frames by 20.

### "too slow"

- Decrease spawn_interval by 20% (minimum 20).
- Increase speed by 10%.
- Decrease grace_frames by 20 (minimum 30).

### "boring" (not enough variety)

- Increase spawn rate by 10%.
- Add a second threat type.
- Narrow the gap by 10 pixels or add more enemies.

### "frustrating" (unfair deaths)

- Increase grace_frames by 60.
- Make hitboxes more forgiving: increase gap by 20 pixels.
- Ensure the cause of death is always visible on screen.

## Validation Checklist

1. **Survive 5 seconds on Easy**: A passive player must survive at least 5 seconds on Easy.
2. **Score 10 on Normal**: A moderately skilled player must score at least 10 points on Normal.
3. **No crash during gameplay**: Run at Normal difficulty for at least 60 seconds. No exceptions.
4. **Tiers differ measurably**: Each tier must differ by at least 20% in at least two parameters.
5. **Grace period works**: No damage during grace period.
6. **Restart is instant**: SPACE or R must immediately restart with no visible delay.
