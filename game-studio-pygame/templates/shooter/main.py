"""Space Blaster - PyGame shooter template."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

import pygame

from pygame_sdk import Renderer, SceneState
from model import ShooterModel
from view import render


def main():
    model = ShooterModel()
    renderer = Renderer(model.config.screen_width, model.config.screen_height, model.config.fps)

    headless = os.environ.get("SDL_VIDEODRIVER") == "dummy"
    if headless:
        renderer.init_headless()
    else:
        renderer.init()

    model.renderer = renderer
    model.scene.transition(SceneState.MENU)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                model.handle_event(event)

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
