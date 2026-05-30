from __future__ import annotations

import pygame

from pygame_sdk import SceneState
from pygame_sdk.styles import WHITE, SCORE_COLOR, HINT_COLOR, GRACE_COLOR, TITLE_FG
from config import ContraConfig


def _cam_offset(cam, wx, wy, sw, sh):
    """Convert world coords to screen coords using camera."""
    sx = int(wx - cam.position.x + sw / 2)
    sy = int(wy - cam.position.y + sh / 2)
    return sx, sy


def _on_screen(sx, sy, sw, sh, margin=64):
    return -margin < sx < sw + margin and -margin < sy < sh + margin


def render(model, renderer):
    renderer.clear(model.config.bg_color)
    screen = renderer.screen
    if screen is None:
        return

    sw, sh = renderer.width, renderer.height
    cfg: ContraConfig = model.config
    ts = cfg.tile_size

    # --- MENU ---
    if model.scene.is_state(SceneState.MENU):
        renderer.draw_title(cfg.name.upper())
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", 260, SCORE_COLOR)
        renderer.draw_hint("1=Easy  2=Normal  3=Hard  |  SPACE to start")
        renderer.draw_text_centered("Arrows/WASD: Move  |  SPACE: Shoot", 320, HINT_COLOR, font="small")
        return

    # --- Camera offset ---
    cam = model.camera
    if cam is None:
        return
    cam_x = cam.position.x - sw / 2
    cam_y = cam.position.y - sh / 2

    # --- Draw tiles ---
    tile_col0 = max(0, int(cam_x // ts))
    tile_col1 = min(cfg.level_width, int((cam_x + sw) // ts) + 2)
    tile_row0 = max(0, int(cam_y // ts))
    tile_row1 = min(cfg.level_height, int((cam_y + sh) // ts) + 2)

    for row in range(tile_row0, tile_row1):
        for col in range(tile_col0, tile_col1):
            ch = model._tile_at(col, row)
            sx = int(col * ts - cam_x)
            sy = int(row * ts - cam_y)
            if ch == "#":
                pygame.draw.rect(screen, cfg.ground_color, (sx, sy, ts, ts))
                # Texture lines
                pygame.draw.line(screen, (80, 55, 30), (sx, sy + ts // 2), (sx + ts, sy + ts // 2))
                pygame.draw.line(screen, (80, 55, 30), (sx + ts // 2, sy), (sx + ts // 2, sy + ts))
            elif ch == "=":
                pygame.draw.rect(screen, cfg.platform_color, (sx, sy, ts, ts // 3))
                pygame.draw.line(screen, (90, 75, 55), (sx, sy), (sx + ts, sy))
            elif ch == "F":
                pygame.draw.rect(screen, (255, 215, 0), (sx, sy, ts, ts))
                pygame.draw.rect(screen, (200, 170, 0), (sx, sy, ts, ts), 2)

    # --- Draw pickups ---
    for p in model.pickup_states:
        if not p["active"]:
            continue
        sx, sy = _cam_offset(cam, p["x"], p["y"], sw, sh)
        if not _on_screen(sx, sy, sw, sh):
            continue
        pw, ph = p["size"]
        pygame.draw.rect(screen, p["color"], (sx, sy, pw, ph))
        # Plus sign
        pygame.draw.line(screen, WHITE, (sx + pw // 2, sy + 2), (sx + pw // 2, sy + ph - 2))
        pygame.draw.line(screen, WHITE, (sx + 2, sy + ph // 2), (sx + pw - 2, sy + ph // 2))

    # --- Draw enemies ---
    for e in model.enemy_states:
        if not e["active"]:
            continue
        sx, sy = _cam_offset(cam, e["x"], e["y"], sw, sh)
        if not _on_screen(sx, sy, sw, sh):
            continue
        ew, eh = e["size"]
        pygame.draw.rect(screen, e["color"], (sx, sy, ew, eh))
        # Eyes
        pygame.draw.rect(screen, WHITE, (sx + 4, sy + 6, 4, 4))
        pygame.draw.rect(screen, WHITE, (sx + ew - 8, sy + 6, 4, 4))
        # HP bar for multi-hp enemies
        if e["max_hp"] > 1:
            bar_w = int(ew * e["hp"] / e["max_hp"])
            pygame.draw.rect(screen, (50, 200, 50), (sx, sy - 5, bar_w, 3))

    # --- Draw bullets ---
    for b in model.bullets:
        if not b.active:
            continue
        sx, sy = _cam_offset(cam, b.x, b.y, sw, sh)
        if not _on_screen(sx, sy, sw, sh, 32):
            continue
        pygame.draw.rect(screen, b.color, (sx, sy, b.size[0], b.size[1]))

    # --- Draw player ---
    pw, ph = cfg.player_size
    psx, psy = _cam_offset(cam, model.player_x, model.player_y, sw, sh)
    pygame.draw.rect(screen, cfg.player_color, (psx, psy, pw, ph))
    # Gun
    if model.facing_right:
        pygame.draw.rect(screen, (180, 180, 180), (psx + pw, psy + 10, 6, 4))
    else:
        pygame.draw.rect(screen, (180, 180, 180), (psx - 6, psy + 10, 6, 4))
    # Head
    pygame.draw.rect(screen, (255, 200, 150), (psx + 4, psy + 2, pw - 8, 10))

    # --- HUD ---
    renderer.draw_score(model.score.current)
    renderer.draw_text(f"HP: {model.player_hp}", 10, 10, (200, 50, 50))
    # Direction indicator
    arrow = ">>>" if model.facing_right else "<<<"
    renderer.draw_text(arrow, 10, 30, (100, 200, 100), font="small")

    # Grace period
    grace = model.params.get("grace_period", 120)
    remaining = max(0, grace - model.frame)
    if remaining > 0:
        renderer.draw_grace_indicator(remaining)

    # --- Game Over / Win overlay ---
    if model.scene.is_state(SceneState.GAME_OVER):
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        if model.won:
            renderer.draw_text_centered("VICTORY!", sh // 3, (255, 215, 0), font="large")
        else:
            renderer.draw_text_centered("GAME OVER", sh // 3, (255, 80, 80), font="large")

        renderer.draw_text_centered(f"Score: {model.score.current}", sh // 2, WHITE)
        renderer.draw_text_centered(f"Best: {model.score.best}", sh // 2 + 30, SCORE_COLOR)
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", sh // 2 + 70, SCORE_COLOR, font="small")
        renderer.draw_text_centered("Press R to restart", sh // 2 + 100, HINT_COLOR, font="small")
