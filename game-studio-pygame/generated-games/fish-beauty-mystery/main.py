"""《相府鱼美人》场景渲染入口

纯视觉渲染器，接收 stdin JSON 指令，通过 game_stream_runner.py 流式传输帧。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

import pygame

from scenes import SceneRenderer, W, H

# Handle CJK font
_CJK_CANDIDATES = [
    "pingfangsc", "hiraginosansgb", "stheitimedium",
    "notosanscjksc", "arialunicodems", "microsoftyahei",
    "wenquanyimicrohei", "droidsansfallback",
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))

    # Override fonts with CJK
    available = pygame.font.get_fonts()
    cjk_font = None
    for c in _CJK_CANDIDATES:
        if c in available:
            cjk_font = c
            break

    renderer = SceneRenderer(screen)
    clock = pygame.time.Clock()

    # Stdin reader thread for scene commands
    import json
    import threading

    def stdin_reader():
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg_type = msg.get("type")
            if msg_type == "scene":
                renderer.queue_scene(msg.get("scene", "title"))
            elif msg.get("scene"):
                renderer.queue_scene(msg.get("scene", "title"))

    reader_thread = threading.Thread(target=stdin_reader, daemon=True)
    reader_thread.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break

        renderer.draw()
        pygame.display.flip()
        clock.tick(15)

    pygame.quit()


if __name__ == "__main__":
    main()
