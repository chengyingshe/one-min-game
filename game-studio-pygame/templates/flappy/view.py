from __future__ import annotations

from pygame_sdk.styles import (
    WHITE, SCORE_COLOR, HINT_COLOR, GRACE_COLOR, TITLE_FG, GAMEOVER_FG,
)
from pygame_sdk import SceneState


def render(model, renderer):
    renderer.clear(model.config.bg_color)

    if model.scene.is_state(SceneState.MENU):
        renderer.draw_title(model.config.name.upper())
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", 260, SCORE_COLOR)
        renderer.draw_hint("1=Easy  2=Normal  3=Hard  |  SPACE to start")
        return

    if model.scene.is_state(SceneState.GAME_OVER):
        for pipe in model.pipes:
            _draw_pipe(pipe, renderer)
        renderer.draw_game_over(model.score.current, model.score.best)
        renderer.draw_text_centered(f"[{model.difficulty.upper()}]", model.renderer.height // 2 + 110, SCORE_COLOR, font="small")
        return

    for pipe in model.pipes:
        _draw_pipe(pipe, renderer)

    pw, ph = model.config.player_size
    renderer.draw_rect(
        int(model.player_x), int(model.player_y),
        pw, ph, model.config.player_color,
    )

    ground_y = model.config.screen_height - model.config.ground_height
    renderer.draw_rect(0, ground_y, model.config.screen_width, model.config.ground_height, model.config.ground_color)

    renderer.draw_score(model.score.current)

    grace = model.params.get("grace_period", 90)
    remaining = max(0, grace - model.frame)
    if remaining > 0:
        renderer.draw_grace_indicator(remaining)


def _draw_pipe(pipe, renderer):
    tx, ty, tw, th = pipe.top_rect
    renderer.draw_rect(int(tx), int(ty), int(tw), int(th), pipe.color)
    bx, by, bw, bh = pipe.bottom_rect
    renderer.draw_rect(int(bx), int(by), int(bw), int(bh), pipe.color)
