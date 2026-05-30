"""Zombie FPS — entry point."""

import os
import sys

# Ensure SDK is importable for local dev
_sdk = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "runtime", "pygame-sdk")
if os.path.isdir(_sdk) and _sdk not in sys.path:
    sys.path.insert(0, _sdk)

import pygame
from config import load_config
from model import GameModel


def main():
    cfg = load_config()
    w, h, fps = cfg["screen"]["width"], cfg["screen"]["height"], cfg["screen"]["fps"]

    pygame.init()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Zombie FPS")
    clock = pygame.time.Clock()

    model = GameModel(cfg)

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            model.handle_event(ev)

        model.update()
        model.render(screen)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
