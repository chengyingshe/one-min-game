"""游戏入口"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

import pygame

from pygame_sdk import Renderer
from model import GameModel
from view import GameView


def main():
    renderer = Renderer(800, 600, 30)
    renderer.init()

    # Override fonts with Chinese-capable system fonts
    _CJK_CANDIDATES = [
        "pingfangsc", "hiraginosansgb", "stheitimedium",
        "stheitilight", "songti", "arialunicodems",
        "notosanscjksc", "microsoftyahei", "simsun",
        "wenquanyimicrohei", "droidsansfallback",
    ]
    available = pygame.font.get_fonts()
    cjk_font = None
    for c in _CJK_CANDIDATES:
        if c in available:
            cjk_font = c
            break
    if cjk_font:
        renderer._font = pygame.font.SysFont(cjk_font, 20)
        renderer._font_large = pygame.font.SysFont(cjk_font, 36)
        renderer._font_small = pygame.font.SysFont(cjk_font, 16)
    model = GameModel()
    view = GameView(renderer)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

                key_map = {
                    pygame.K_UP: "up",
                    pygame.K_DOWN: "down",
                    pygame.K_LEFT: "left",
                    pygame.K_RIGHT: "right",
                    pygame.K_RETURN: "primary",
                    pygame.K_SPACE: "secondary",
                    pygame.K_w: "up",
                    pygame.K_s: "down",
                    pygame.K_a: "left",
                    pygame.K_d: "right",
                }
                action = key_map.get(event.key)
                if action:
                    model.handle_event("action", action)

        view.draw(model)
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
