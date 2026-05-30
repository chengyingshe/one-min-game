from __future__ import annotations

from pygame_sdk.styles import WHITE, SCORE_COLOR, HINT_COLOR, GRACE_COLOR
from pygame_sdk import SceneState


def render(model, renderer):
    renderer.clear(model.config.bg_color)

    if model.scene.is_state(SceneState.MENU):
        renderer.draw_title(model.config.name.upper())
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", 260, SCORE_COLOR)
        renderer.draw_hint("1=Easy  2=Normal  3=Hard  |  SPACE to start")
        return

    if model.scene.is_state(SceneState.GAME_OVER):
        _draw_world(model, renderer)
        renderer.draw_game_over(model.score.current, model.score.best)
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", model.renderer.height // 2 + 110, SCORE_COLOR, font="small")
        return

    _draw_world(model, renderer)

    pw, ph = model.config.player_size
    renderer.draw_rect(int(model.player_x), int(model.player_y), pw, ph, model.config.player_color)

    renderer.draw_score(model.score.current)
    renderer.draw_text(f"HP: {model.player_hp}", 10, 10, (200, 50, 50))

    grace = model.params.get("grace_period", 90)
    remaining = max(0, grace - model.frame)
    if remaining > 0:
        renderer.draw_grace_indicator(remaining)


def _draw_world(model, renderer):
    for plat in model.platforms:
        renderer.draw_rect(int(plat.x), int(plat.y), plat.width, plat.height, plat.color)
    for e in model.enemies:
        if e.active:
            renderer.draw_rect(int(e.x), int(e.y), e.size[0], e.size[1], e.color)
    for c in model.coins:
        if c.active:
            renderer.draw_rect(int(c.x), int(c.y), c.size[0], c.size[1], c.color)
