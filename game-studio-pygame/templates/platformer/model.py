from __future__ import annotations

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

from pygame_sdk import SceneManager, ScoreManager, SceneState
from config import PlatformerConfig, load_config


class Platform:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color


class Enemy:
    def __init__(self, x, y, speed, size, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.color = color
        self.direction = random.choice([-1, 1])
        self.active = True

    def update(self, platforms):
        self.x += self.speed * self.direction
        if self.x < 0 or self.x > 776:
            self.direction *= -1


class Coin:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.active = True


class PlatformerModel:
    def __init__(self):
        self.config = load_config()
        self.scene = SceneManager()
        self.score = ScoreManager()
        self.difficulty: str = "normal"
        self.frame: int = 0
        self.params: dict = {}
        self.player_x: float = 100
        self.player_y: float = 400
        self.player_vy: float = 0
        self.player_hp: int = 3
        self.on_ground: bool = False
        self.platforms: list[Platform] = []
        self.enemies: list[Enemy] = []
        self.coins: list[Coin] = []
        self.renderer = None

    def _get_params(self) -> dict:
        return self.config.params(self.difficulty)

    def reset(self):
        self.frame = 0
        self.params = self._get_params()
        self.player_x = 100
        self.player_y = 400
        self.player_vy = 0
        self.player_hp = self.params.get("player_hp", 3)
        self.on_ground = False
        self.score.reset()
        self.enemies.clear()
        self.coins.clear()
        self._generate_level()
        self.scene.transition(SceneState.GAMEPLAY)

    def _generate_level(self):
        self.platforms = []
        self.platforms.append(Platform(0, 560, 800, 40, self.config.ground_color))

        random.seed(42)
        y_positions = [440, 360, 280, 200, 140]
        for y in y_positions:
            for _ in range(random.randint(2, 3)):
                x = random.randint(0, 650)
                w = random.randint(80, 160)
                self.platforms.append(Platform(x, y, w, 16, self.config.platform_color))
                if random.random() < 0.5:
                    self.coins.append(Coin(x + w // 2, y - 20, self.config.coin_size, self.config.coin_color))

        spawn_rate = self.params.get("spawn_rate", 100)
        for plat in self.platforms[1:]:
            if random.random() < 0.3:
                es = self.params.get("enemy_speed", 2.0)
                self.enemies.append(Enemy(plat.x + 10, plat.y - self.config.enemy_size[1], es, self.config.enemy_size, self.config.enemy_color))

    def handle_event(self, event):
        import pygame
        if event.type != pygame.KEYDOWN:
            return

        if self.scene.is_state(SceneState.MENU):
            if event.key == pygame.K_SPACE:
                self.reset()
            elif event.key == pygame.K_1:
                self.difficulty = "easy"
            elif event.key == pygame.K_2:
                self.difficulty = "normal"
            elif event.key == pygame.K_3:
                self.difficulty = "hard"
        elif self.scene.is_state(SceneState.GAME_OVER):
            if event.key in (pygame.K_SPACE, pygame.K_r):
                self.reset()
        elif self.scene.is_playing():
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.on_ground:
                    impulse = self.params.get("jump_impulse", -13)
                    self.player_vy = impulse
                    self.on_ground = False

    def update(self):
        if not self.scene.is_playing():
            return

        import pygame
        self.frame += 1
        self.params = self._get_params()

        keys = pygame.key.get_pressed()
        speed = self.params.get("player_speed", 5)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x = max(0, self.player_x - speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x = min(self.config.screen_width - self.config.player_size[0], self.player_x + speed)

        gravity = self.params.get("gravity", 0.6)
        self.player_vy += gravity
        self.player_y += self.player_vy

        self.on_ground = False
        pw, ph = self.config.player_size
        for plat in self.platforms:
            if (self.player_vy >= 0 and
                self.player_x + pw > plat.x and
                self.player_x < plat.x + plat.width and
                self.player_y + ph >= plat.y and
                self.player_y + ph <= plat.y + plat.height + self.player_vy + 2):
                self.player_y = plat.y - ph
                self.player_vy = 0
                self.on_ground = True

        if self.player_y > self.config.screen_height:
            self.player_hp -= 1
            if self.player_hp <= 0:
                self.score.update_best()
                self.scene.transition(SceneState.GAME_OVER)
                return
            self.player_x = 100
            self.player_y = 400
            self.player_vy = 0

        for e in self.enemies:
            e.update(self.platforms)

        grace = self.params.get("grace_period", 90)
        if self.frame > grace:
            for e in self.enemies:
                if e.active and self._rects_overlap(self.player_x, self.player_y, pw, ph, e.x, e.y, e.size[0], e.size[1]):
                    self.player_hp -= 1
                    e.active = False
                    if self.player_hp <= 0:
                        self.score.update_best()
                        self.scene.transition(SceneState.GAME_OVER)
                        return

        for c in self.coins:
            if c.active and self._rects_overlap(self.player_x, self.player_y, pw, ph, c.x, c.y, c.size[0], c.size[1]):
                c.active = False
                self.score.add(1)

    @staticmethod
    def _rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
