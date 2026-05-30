from __future__ import annotations

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

from pygame_sdk import Entity, EntityStore, SceneManager, ScoreManager, Vector2D, EntityType, SceneState
from config import FlappyConfig, load_config


class Pipe:
    def __init__(self, x: int, gap_y: int, gap_size: int, width: int, color: tuple):
        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.width = width
        self.color = color
        self.scored = False

    @property
    def top_rect(self):
        return (self.x, 0, self.width, self.gap_y)

    @property
    def bottom_rect(self):
        return (self.x, self.gap_y + self.gap_size, self.width, 600)

    def collides(self, px, py, pw, ph) -> bool:
        if px + pw > self.x and px < self.x + self.width:
            if py < self.gap_y or py + ph > self.gap_y + self.gap_size:
                return True
        return False


class FlappyModel:
    def __init__(self):
        self.config: FlappyConfig = load_config()
        self.scene = SceneManager()
        self.score = ScoreManager()
        self.difficulty: str = "normal"
        self.frame: int = 0
        self.pipes: list[Pipe] = []
        self.player_x: float = 100
        self.player_y: float = self.config.screen_height / 2
        self.player_vy: float = 0
        self.params: dict = {}
        self.renderer = None

    def _get_params(self) -> dict:
        return self.config.params(self.difficulty)

    def reset(self):
        self.frame = 0
        self.pipes.clear()
        self.player_y = self.config.screen_height / 2
        self.player_vy = 0
        self.score.reset()
        self.params = self._get_params()
        self.scene.transition(SceneState.GAMEPLAY)

    def spawn_pipe(self):
        gap = self.params.get("pipe_gap", 180)
        min_y = 80
        max_y = self.config.screen_height - self.config.ground_height - gap - 80
        gap_y = random.randint(min_y, max(1, max_y))
        x = self.config.screen_width + 10
        self.pipes.append(Pipe(x, gap_y, gap, self.config.pipe_width, self.config.pipe_color))

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
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                impulse = self.params.get("flap_impulse", -10)
                self.player_vy = impulse

    def update(self):
        if not self.scene.is_playing():
            return

        self.frame += 1
        self.params = self._get_params()

        gravity = self.params.get("gravity", 0.5)
        self.player_vy += gravity
        self.player_y += self.player_vy

        ground = self.config.screen_height - self.config.ground_height
        if self.player_y + self.config.player_size[1] >= ground:
            self.player_y = ground - self.config.player_size[1]
            self._die()
            return
        if self.player_y < 0:
            self.player_y = 0
            self.player_vy = 0

        pipe_speed = self.params.get("pipe_speed", 3)
        for pipe in self.pipes:
            pipe.x -= pipe_speed

        self.pipes = [p for p in self.pipes if p.x + p.width > -10]

        spawn_interval = self.params.get("spawn_interval", 70)
        if self.frame % spawn_interval == 0:
            self.spawn_pipe()

        grace = self.params.get("grace_period", 90)
        if self.frame > grace:
            pw, ph = self.config.player_size
            for pipe in self.pipes:
                if pipe.collides(self.player_x, self.player_y, pw, ph):
                    self._die()
                    return
                if not pipe.scored and pipe.x + pipe.width < self.player_x:
                    pipe.scored = True
                    self.score.add(1)

    def _die(self):
        self.score.update_best()
        self.scene.transition(SceneState.GAME_OVER)
