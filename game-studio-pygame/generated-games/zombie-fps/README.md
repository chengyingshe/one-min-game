# zombie-fps

> FPS (raycasting)

**Session duration**: 60s

## Controls

- `W/S or Up/Down` -- Forward/Back
- `A/D or Left/Right` -- Turn
- `Space` -- Shoot
- `1/2/3` -- Difficulty select
- `Q / Esc` -- Quit

- `R` / `Space` (Game Over) -- Restart
- `Q` / `Esc` -- Quit

## Difficulty

| Tier | Parameters |
|------|------------|
| easy | HP 7  Enemy speed 0.018  Enemies 3  Enemy HP 1 |
| normal | HP 5  Enemy speed 0.025  Enemies 5  Enemy HP 2 |
| hard | HP 3  Enemy speed 0.035  Enemies 8  Enemy HP 3 |

## Run

```bash
cd generated-games/zombie-fps && python3 main.py
```

## Display

- Resolution: 800x600
- Requires: PyGame 2.5+

## Project structure

```
zombie-fps/
|-- config.py
|-- main.py
|-- model.py
|-- config.yaml
|-- requirements.txt
|-- screenshot.png
|-- screenshot_6s.png
|-- screenshot_clean.png
```

## Tech stack

- PyGame -- Graphics and input
- pygame-sdk -- Game engine (physics, collision, rendering, AI, scenes)
- Python 3.11+
