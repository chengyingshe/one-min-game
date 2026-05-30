from __future__ import annotations

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

from pygame_sdk import SceneManager, ScoreManager, SceneState
from config import ShooterConfig, load_config


class Bullet:
    def __init__(self, x, y, speed, color, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.size = size
        self.active = True

    def update(self):
        self.y -= self.speed
        if self.y + self.size[1] < 0:
            self.active = False


class Enemy:
    def __init__(self, x, y, speed, color, size, hp=1):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.size = size
        self.hp = hp
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > 650:
            self.active = False


class ShooterModel:
    def __init__(self):
        self.config = load_config()
        self.scene = SceneManager()
        self.score = ScoreManager()
        self.difficulty: str = "normal"
        self.frame: int = 0
        self.params: dict = {}
        self.player_x: float = self.config.screen_width / 2
        self.player_y: float = self.config.screen_height - 60
        self.player_hp: int = 4
        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.shoot_cooldown: int = 0
        self.renderer = None

    def _get_params(self) -> dict:
        return self.config.params(self.difficulty)

    def reset(self):
        self.frame = 0
        self.params = self._get_params()
        self.player_x = self.config.screen_width / 2
        self.player_y = self.config.screen_height - 60
        self.player_hp = self.params.get("player_hp", 4)
        self.bullets.clear()
        self.enemies.clear()
        self.shoot_cooldown = 0
        self.score.reset()
        self.scene.transition(SceneState.GAMEPLAY)

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

    def update(self):
        if not self.scene.is_playing():
            return

        import pygame
        self.frame += 1
        self.params = self._get_params()

        keys = pygame.key.get_pressed()
        speed = self.config.player_size[0] * 0.6
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x = max(0, self.player_x - speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x = min(self.config.screen_width - self.config.player_size[0], self.player_x + speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_y = max(0, self.player_y - speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_y = min(self.config.screen_height - self.config.player_size[1], self.player_y + speed)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            bs = self.params.get("bullet_speed", 5)
            bx = self.player_x + self.config.player_size[0] / 2 - self.config.bullet_size[0] / 2
            by = self.player_y - self.config.bullet_size[1]
            self.bullets.append(Bullet(bx, by, bs, self.config.bullet_color, self.config.bullet_size))
            self.shoot_cooldown = 10

        for b in self.bullets:
            b.update()
        for e in self.enemies:
            e.update()
        self.bullets = [b for b in self.bullets if b.active]
        self.enemies = [e for e in self.enemies if e.active]

        spawn_rate = self.params.get("spawn_rate", 65)
        if self.frame % spawn_rate == 0:
            es = self.params.get("enemy_speed", 3.0)
            ex = random.randint(0, self.config.screen_width - self.config.enemy_size[0])
            self.enemies.append(Enemy(ex, -self.config.enemy_size[1], es, self.config.enemy_color, self.config.enemy_size))

        for b in self.bullets:
            if not b.active:
                continue
            for e in self.enemies:
                if not e.active:
                    continue
                if self._rects_overlap(b.x, b.y, b.size[0], b.size[1], e.x, e.y, e.size[0], e.size[1]):
                    b.active = False
                    e.hp -= 1
                    if e.hp <= 0:
                        e.active = False
                        self.score.add(1)

        grace = self.params.get("grace_period", 90)
        if self.frame > grace:
            pw, ph = self.config.player_size
            for e in self.enemies:
                if e.active and self._rects_overlap(self.player_x, self.player_y, pw, ph, e.x, e.y, e.size[0], e.size[1]):
                    self.player_hp -= 1
                    e.active = False
                    if self.player_hp <= 0:
                        self.score.update_best()
                        self.scene.transition(SceneState.GAME_OVER)
                        return

    @staticmethod
    def _rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
