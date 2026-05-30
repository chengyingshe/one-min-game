"""Rendering for Wild Survivors."""
from __future__ import annotations

import math

from pygame_sdk import Renderer, SceneState

from model import WildSurvivorsModel, EnemyState


# Colors
GRASS_COLOR = (76, 153, 0)
GRASS_DARK = (68, 136, 0)
HP_BAR_BG = (60, 0, 0)
HP_BAR_FG = (0, 200, 0)
HUD_BG = (0, 0, 0, 180)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)


def render(model: WildSurvivorsModel, renderer: Renderer) -> None:
    """Render the current game state."""
    if renderer.screen is None:
        return

    if model.scene.is_state(SceneState.MENU):
        _render_menu(model, renderer)
        return

    if model.scene.is_state(SceneState.GAME_OVER):
        _render_gameplay(model, renderer)
        _render_game_over(model, renderer)
        return

    _render_gameplay(model, renderer)


def _render_menu(model: WildSurvivorsModel, renderer: Renderer) -> None:
    """Draw the main menu."""
    renderer.clear((20, 20, 30))
    renderer.draw_text_centered("WILD SURVIVORS", 120, (255, 220, 50), font="large")
    renderer.draw_text_centered("Cooperative Survival", 170, (180, 180, 180), font="small")

    renderer.draw_text_centered("Select Difficulty:", 250, WHITE)

    colors = {"easy": (0, 255, 0), "normal": (255, 255, 0), "hard": (255, 68, 68)}
    y = 290
    for tier in ("easy", "normal", "hard"):
        label = f"[{tier.upper()[0]}] {tier.capitalize()}"
        col = colors.get(tier, WHITE)
        if model.difficulty_name == tier:
            label = "> " + label + " <"
            renderer.draw_rect(renderer.width // 2 - 140, y - 2, 280, 28, (50, 50, 70))
        renderer.draw_text_centered(label, y, col)
        y += 40

    renderer.draw_text_centered("Press ENTER to Start", 450, (200, 200, 200))
    renderer.draw_text_centered(
        "WASD/Arrows: Move | Space: Attack | E: Wall | R: Campfire",
        500, (120, 120, 120), font="small",
    )
    renderer.draw_text_centered(
        "Harvest resources, build defenses, survive together!",
        530, (100, 100, 100), font="small",
    )


def _render_gameplay(model: WildSurvivorsModel, renderer: Renderer) -> None:
    """Draw the main gameplay view."""
    renderer.clear(GRASS_COLOR)

    sw, sh = renderer.width, renderer.height
    ts = model.config.tile_size
    cam = model.camera

    # Camera offset (top-left of viewport in world coords)
    cam_x = cam.position.x - sw / 2
    cam_y = cam.position.y - sh / 2

    # Clamp camera
    world_pw = model.config.world_width * ts
    world_ph = model.config.world_height * ts
    cam_x = max(0, min(cam_x, world_pw - sw))
    cam_y = max(0, min(cam_y, world_ph - sh))

    # Draw visible tile grid (grass with subtle pattern)
    start_tx = max(0, int(cam_x // ts))
    start_ty = max(0, int(cam_y // ts))
    end_tx = min(model.config.world_width, start_tx + sw // ts + 2)
    end_ty = min(model.config.world_height, start_ty + sh // ts + 2)

    for ty in range(start_ty, end_ty):
        for tx in range(start_tx, end_tx):
            sx = int(tx * ts - cam_x)
            sy = int(ty * ts - cam_y)
            color = GRASS_COLOR if (tx + ty) % 2 == 0 else GRASS_DARK
            if model.tile_grid[ty][tx] != 0:
                # Blocked tiles slightly darker
                color = (50, 100, 0)
            renderer.draw_rect(sx, sy, ts, ts, color)

    # Draw resources
    for r in model.resources:
        if not r.active:
            continue
        sx, sy, vis = cam.world_to_screen(r.pos, sw, sh)
        if not vis:
            # Check if partially visible
            sx = int(r.pos.x - cam_x)
            sy = int(r.pos.y - cam_y)
            if sx + ts < 0 or sx > sw or sy + ts < 0 or sy > sh:
                continue
        else:
            sx = int(r.pos.x - cam_x)
            sy = int(r.pos.y - cam_y)

        rtype = r.tags.get("resource_type", "")
        if rtype == "tree":
            # Tree: brown trunk + green circle canopy
            cx = sx + ts // 2
            cy = sy + ts // 2
            renderer.draw_rect(sx + ts // 3, sy + ts // 2, ts // 3, ts // 2, (100, 60, 20))
            _draw_circle(renderer, cx, cy - 2, ts // 3, (34, 139, 34))
        elif rtype == "rock":
            renderer.draw_rect(sx + 1, sy + 1, ts - 2, ts - 2, (150, 150, 150))
        elif rtype == "ore":
            # Gold diamond shape
            cx = sx + ts // 2
            cy = sy + ts // 2
            hs = ts // 3
            renderer.draw_rect(cx - hs, cy - hs, hs * 2, hs * 2, (200, 170, 50))
            renderer.draw_rect(cx - hs + 1, cy - hs + 1, hs * 2 - 2, hs * 2 - 2, (220, 190, 70))

        # HP bar for damaged resources
        if r.hp < r.max_hp:
            _draw_hp_bar(renderer, sx, sy - 4, ts, r.hp, r.max_hp)

    # Draw structures
    for s in model.structures:
        if not s.active:
            continue
        sx = int(s.pos.x - cam_x)
        sy = int(s.pos.y - cam_y)
        if sx + ts < 0 or sx > sw or sy + ts < 0 or sy > sh:
            continue

        stype = s.tags.get("structure_type", "")
        if stype == "wall":
            renderer.draw_rect(sx, sy, ts, ts, (139, 90, 43))
            renderer.draw_rect(sx + 1, sy + 1, ts - 2, ts - 2, (160, 110, 55))
        elif stype == "campfire":
            renderer.draw_rect(sx + 2, sy + 2, ts - 4, ts - 4, (255, 140, 0))
            _draw_circle(renderer, sx + ts // 2, sy + ts // 2, ts // 4, (255, 200, 50))

        if s.hp < s.max_hp:
            _draw_hp_bar(renderer, sx, sy - 4, ts, s.hp, s.max_hp)

    # Draw enemies
    for es in model.enemies:
        if not es.entity.active:
            continue
        ex = int(es.entity.pos.x - cam_x)
        ey = int(es.entity.pos.y - cam_y)
        if ex + ts < 0 or ex > sw or ey + ts < 0 or ey > sh:
            continue

        _draw_circle(renderer, ex + ts // 2, ey + ts // 2, ts // 2 - 1, es.entity.color)
        # Symbol
        renderer.draw_text(es.entity.symbol, ex + 2, ey, DARK_GRAY, font="small")

        # HP bar
        _draw_hp_bar(renderer, ex, ey - 4, ts, es.entity.hp, es.entity.max_hp)

    # Draw players
    for pid, ps in model.players.items():
        if not ps.alive:
            continue
        px = int(ps.entity.pos.x - cam_x)
        py = int(ps.entity.pos.y - cam_y)

        # Player body
        renderer.draw_rect(px + 1, py + 1, ts - 2, ts - 2, ps.entity.color)
        # Border
        renderer.draw_rect(px, py, ts, ts, WHITE, filled=False)
        # Player number
        renderer.draw_text(ps.name, px + 1, py + 1, (0, 0, 0), font="small")

        # Facing direction indicator
        fx = int(ps.facing.x * ts * 0.6)
        fy = int(ps.facing.y * ts * 0.6)
        ind_x = px + ts // 2 + fx - 2
        ind_y = py + ts // 2 + fy - 2
        renderer.draw_rect(ind_x, ind_y, 4, 4, WHITE)

        # HP bar
        _draw_hp_bar(renderer, px, py - 6, ts, ps.entity.hp, ps.entity.max_hp)

    # HUD
    _render_hud(model, renderer)

    # Grace period indicator
    if model.grace_frames > 0:
        secs = model.grace_frames // 60 + 1
        renderer.draw_text_centered(f"Safe Zone: {secs}s", 30, (0, 255, 0), font="small")


def _render_hud(model: WildSurvivorsModel, renderer: Renderer) -> None:
    """Draw the heads-up display."""
    sw = renderer.width

    # Top HUD bar background
    renderer.draw_rect(0, 0, sw, 50, (0, 0, 0))

    # Survival timer
    time_text = f"Survived: {model.score.current}s"
    renderer.draw_text(time_text, 10, 5, (255, 255, 255))

    # Difficulty
    diff_colors = {"easy": (0, 255, 0), "normal": (255, 255, 0), "hard": (255, 68, 68)}
    renderer.draw_text(
        model.difficulty_name.upper(),
        10, 28, diff_colors.get(model.difficulty_name, WHITE), font="small",
    )

    # Per-player info
    x_offset = 200
    for pid, ps in model.players.items():
        if not ps.alive:
            renderer.draw_text(f"{ps.name}: DEAD", x_offset, 5, (120, 60, 60), font="small")
        else:
            # Name + HP
            renderer.draw_text(
                f"{ps.name} HP:{ps.entity.hp}/{ps.entity.max_hp}",
                x_offset, 5, ps.entity.color, font="small",
            )
            # Inventory
            inv = ps.inventory
            inv_text = f"W:{inv['wood']} S:{inv['stone']} I:{inv['iron']}"
            renderer.draw_text(inv_text, x_offset, 28, (180, 180, 180), font="small")
        x_offset += 190

    # Enemy count
    alive_enemies = sum(1 for es in model.enemies if es.entity.active)
    renderer.draw_text(f"Enemies: {alive_enemies}", sw - 120, 5, (255, 100, 100), font="small")

    # Controls hint
    renderer.draw_text("Space:Atk E:Wall R:Fire", sw - 170, 28, (100, 100, 100), font="small")


def _render_game_over(model: WildSurvivorsModel, renderer: Renderer) -> None:
    """Draw game over overlay."""
    import pygame
    if renderer.screen is not None:
        overlay = pygame.Surface((renderer.width, renderer.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        renderer.screen.blit(overlay, (0, 0))

    renderer.draw_text_centered("ALL PLAYERS DEAD", 200, (255, 80, 80), font="large")
    renderer.draw_text_centered(
        f"Survived: {model.score.current}s | Best: {model.score.best}s",
        280, WHITE,
    )
    renderer.draw_text_centered("Press R to return to menu", 340, (150, 150, 150), font="small")


def _draw_circle(renderer: Renderer, cx: int, cy: int, radius: int, color: tuple) -> None:
    """Draw a filled circle using pygame directly."""
    import pygame
    if renderer.screen is None:
        return
    pygame.draw.circle(renderer.screen, color, (cx, cy), max(radius, 1))


def _draw_hp_bar(renderer: Renderer, x: int, y: int, width: int, hp: int, max_hp: int) -> None:
    """Draw a small HP bar above an entity."""
    if max_hp <= 0:
        return
    bar_w = width
    bar_h = 3
    renderer.draw_rect(x, y, bar_w, bar_h, HP_BAR_BG)
    fill = max(0, int(bar_w * hp / max_hp))
    if fill > 0:
        color = HP_BAR_FG if hp > max_hp // 3 else (255, 60, 60)
        renderer.draw_rect(x, y, fill, bar_h, color)
