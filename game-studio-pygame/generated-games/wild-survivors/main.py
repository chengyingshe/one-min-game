"""Wild Survivors - Entry point."""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

import pygame
from pygame_sdk import Renderer, SceneState

from model import WildSurvivorsModel
from view import render


def main():
    model = WildSurvivorsModel()
    renderer = Renderer(model.config.screen_width, model.config.screen_height, model.config.fps)

    headless = os.environ.get("SDL_VIDEODRIVER") == "dummy"
    if headless:
        renderer.init_headless()
    else:
        renderer.init()

    # Detect multiplayer: check injected module-level variable from game_stream_runner
    mp_mode = globals().get("multiplayer_mode")
    is_multiplayer = isinstance(mp_mode, list) and mp_mode[0]

    if is_multiplayer:
        # Wait briefly for player_key_states to be populated by stdin reader
        pks = globals().get("player_key_states", {})
        for _ in range(50):  # up to ~0.5s
            if pks:
                break
            time.sleep(0.01)

        # Auto-start gameplay in multiplayer mode
        model.scene.transition(SceneState.GAMEPLAY)
        model.reset()
    else:
        model.scene.transition(SceneState.MENU)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                model.handle_event(event)

        # Detect late multiplayer activation: when the game started in MENU
        # (because start_game hadn't arrived yet), auto-transition once it does.
        if model.scene.is_state(SceneState.MENU):
            mp_now = globals().get("multiplayer_mode")
            if isinstance(mp_now, list) and mp_now[0]:
                pks = globals().get("player_key_states", {})
                for _ in range(50):
                    if pks:
                        break
                    time.sleep(0.01)
                model.scene.transition(SceneState.GAMEPLAY)
                model.reset()

        model.update()
        render(model, renderer)
        renderer.present()

        capture_frame = int(os.environ.get("CAPTURE_FRAME", "0"))
        capture_path = os.environ.get("CAPTURE_PATH", "")
        if capture_frame > 0 and model.frame == capture_frame and capture_path:
            pygame.image.save(renderer.screen, capture_path)

    renderer.quit()


if __name__ == "__main__":
    main()
