from __future__ import annotations

from pygame_sdk.styles import WHITE, SCORE_COLOR, HINT_COLOR, GRACE_COLOR, TITLE_FG
from pygame_sdk import SceneState


def render(model, renderer):
    renderer.clear(model.config.bg_color)

    if model.scene.is_state(SceneState.MENU):
        renderer.draw_title(model.config.name.upper())
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", 260, SCORE_COLOR)
        renderer.draw_hint("1=Easy  2=Normal  3=Hard  |  SPACE to start")
        return

    if model.scene.is_state(SceneState.GAME_OVER):
        for b in model.bullets:
            renderer.draw_rect(int(b.x), int(b.y), b.size[0], b.size[1], b.color)
        for e in model.enemies:
            renderer.draw_rect(int(e.x), int(e.y), e.size[0], e.size[1], e.color)
        renderer.draw_game_over(model.score.current, model.score.best)
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", model.renderer.height // 2 + 110, SCORE_COLOR, font="small")
        return

    for b in model.bullets:
        renderer.draw_rect(int(b.x), int(b.y), b.size[0], b.size[1], b.color)
    for e in model.enemies:
        renderer.draw_rect(int(e.x), int(e.y), e.size[0], e.size[1], e.color)

    pw, ph = model.config.player_size
    renderer.draw_rect(int(model.player_x), int(model.player_y), pw, ph, model.config.player_color)

    renderer.draw_score(model.score.current)
    renderer.draw_text(f"HP: {model.player_hp}", 10, 10, (200, 50, 50))

    grace = model.params.get("grace_period", 90)
    remaining = max(0, grace - model.frame)
    if remaining > 0:
        renderer.draw_grace_indicator(remaining)
