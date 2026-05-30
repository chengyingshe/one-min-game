from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "pygame-sdk"))

from pygame_sdk import (
    SceneManager, ScoreManager, SceneState,
    Entity, EntityStore, EntityType,
    Camera, Vector2D,
    apply_gravity,
)
from pygame_sdk.camera import CameraMode
from pygame_sdk.collision import Rect
from config import ContraConfig, load_config


def _build_level(config: ContraConfig) -> list[str]:
    """Build the side-scrolling level as a string grid."""
    W, H = config.level_width, config.level_height
    GND = 16  # ground row (bottom 3 rows are ground)

    grid = [["." for _ in range(W)] for _ in range(H)]

    # Ground rows (3 rows at bottom)
    for y in range(GND, H):
        for x in range(W):
            grid[y][x] = "#"

    # --- Section 1: Start zone (cols 0-20) ---
    # Flat ground, safe

    # --- Section 2: First engagement (cols 20-50) ---
    # Small gap at col 35-36
    for y in range(GND, H):
        grid[y][35] = "."
        grid[y][36] = "."

    # --- Section 3: Platform section (cols 50-90) ---
    # Elevated platforms
    for x in range(55, 62):
        grid[12][x] = "="
    for x in range(67, 74):
        grid[10][x] = "="
    for x in range(78, 85):
        grid[13][x] = "="
    # Gap at 60-61 (below second platform)
    for y in range(GND, H):
        grid[y][62] = "."
        grid[y][63] = "."
        grid[y][64] = "."

    # --- Section 4: Gap gauntlet (cols 90-130) ---
    # Multiple gaps
    for y in range(GND, H):
        for x in [93, 94, 95]:
            grid[y][x] = "."
    # Stepping stones
    for x in range(97, 99):
        grid[14][x] = "="
    for x in range(102, 104):
        grid[13][x] = "="
    for x in range(108, 110):
        grid[14][x] = "="
    # Another gap
    for y in range(GND, H):
        for x in range(113, 116):
            grid[y][x] = "."
    for x in range(116, 119):
        grid[12][x] = "="
    # More gaps
    for y in range(GND, H):
        for x in range(122, 125):
            grid[y][x] = "."

    # --- Section 5: Turret alley (cols 130-170) ---
    # Ground with some cover blocks
    for x in range(135, 138):
        grid[14][x] = "#"
        grid[15][x] = "#"
    for x in range(148, 151):
        grid[14][x] = "#"
        grid[15][x] = "#"
    for x in range(158, 161):
        grid[14][x] = "#"
        grid[15][x] = "#"
    # Small gap
    for y in range(GND, H):
        for x in range(140, 142):
            grid[y][x] = "."
    # Elevated platform
    for x in range(145, 150):
        grid[11][x] = "="
    for x in range(155, 160):
        grid[11][x] = "="
    for x in range(165, 170):
        grid[13][x] = "="

    # --- Section 6: Final zone (cols 170-200) ---
    # Ground continues, denser enemies
    for x in range(175, 178):
        grid[13][x] = "="
    for x in range(183, 186):
        grid[12][x] = "="
    for x in range(190, 193):
        grid[13][x] = "="
    # Finish flag position
    for y in range(13, GND):
        grid[y][config.finish_col] = "F"
        grid[y][config.finish_col + 1] = "F"

    return ["".join(row) for row in grid]


def _build_enemy_defs() -> list[dict]:
    """Define enemy spawn positions and types."""
    return [
        # Section 2: First engagement
        {"type": "soldier", "col": 28, "row": 15},
        {"type": "soldier", "col": 42, "row": 15},
        {"type": "soldier", "col": 48, "row": 15},
        # Section 3: Platform section
        {"type": "soldier", "col": 57, "row": 11},
        {"type": "soldier", "col": 70, "row": 9},
        {"type": "turret", "col": 80, "row": 15},
        # Section 4: Gap gauntlet
        {"type": "drone", "col": 95, "row": 8},
        {"type": "drone", "col": 105, "row": 6},
        {"type": "soldier", "col": 117, "row": 11},
        {"type": "drone", "col": 120, "row": 7},
        # Section 5: Turret alley
        {"type": "turret", "col": 132, "row": 15},
        {"type": "soldier", "col": 136, "row": 13},
        {"type": "turret", "col": 152, "row": 15},
        {"type": "soldier", "col": 160, "row": 15},
        {"type": "drone", "col": 145, "row": 5},
        {"type": "drone", "col": 162, "row": 6},
        {"type": "turret", "col": 168, "row": 15},
        # Section 6: Final zone
        {"type": "soldier", "col": 173, "row": 15},
        {"type": "drone", "col": 178, "row": 7},
        {"type": "soldier", "col": 181, "row": 15},
        {"type": "turret", "col": 185, "row": 15},
        {"type": "soldier", "col": 188, "row": 15},
        {"type": "drone", "col": 192, "row": 5},
        {"type": "soldier", "col": 195, "row": 15},
    ]


def _build_pickup_defs() -> list[dict]:
    """Define health pickup positions."""
    return [
        {"col": 40, "row": 15},
        {"col": 70, "row": 9},
        {"col": 103, "row": 12},
        {"col": 135, "row": 15},
        {"col": 156, "row": 10},
        {"col": 185, "row": 11},
    ]


class Bullet:
    __slots__ = ("x", "y", "vx", "vy", "color", "size", "active", "is_player")

    def __init__(self, x, y, vx, vy, color, size, is_player=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.active = True
        self.is_player = is_player

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def rect(self):
        return (self.x, self.y, self.size[0], self.size[1])


class ContraModel:
    def __init__(self):
        self.config = load_config()
        self.scene = SceneManager()
        self.score = ScoreManager()
        self.difficulty: str = "normal"
        self.frame: int = 0
        self.params: dict = {}
        self.renderer = None

        # Player state
        self.player_x: float = 64.0
        self.player_y: float = 400.0
        self.player_vy: float = 0.0
        self.player_hp: int = 3
        self.facing_right: bool = True
        self.on_ground: bool = False
        self.shoot_cd: int = 0

        # World
        self.level_grid: list[str] = []
        self.tile_solid: set = set()
        self.tile_platform: set = set()
        self.tile_finish: set = set()
        self.camera: Camera | None = None

        # Entities
        self.bullets: list[Bullet] = []
        self.enemy_defs: list[dict] = []
        self.enemy_states: list[dict] = []
        self.pickup_states: list[dict] = []
        self.won: bool = False

    def _get_params(self) -> dict:
        return self.config.difficulty.get(self.difficulty, self.config.difficulty["normal"])

    def reset(self):
        self.frame = 0
        self.params = self._get_params()
        self.player_hp = self.params.get("player_hp", self.config.player_hp)
        self.player_x = 64.0
        self.player_y = 400.0
        self.player_vy = 0.0
        self.facing_right = True
        self.on_ground = False
        self.shoot_cd = 0
        self.bullets.clear()
        self.won = False
        self.score.reset()

        # Build level
        self.level_grid = _build_level(self.config)
        self._parse_tiles()

        # Build enemies
        self.enemy_defs = _build_enemy_defs()
        self.enemy_states = []
        for ed in self.enemy_defs:
            ts = self.config.tile_size
            ex = ed["col"] * ts
            ey = ed["row"] * ts
            etype = ed["type"]
            if etype == "soldier":
                hp = self.config.soldier_hp
                color = self.config.soldier_color
                size = self.config.soldier_size
            elif etype == "turret":
                hp = self.config.turret_hp
                color = self.config.turret_color
                size = self.config.turret_size
            else:
                hp = self.config.drone_hp
                color = self.config.drone_color
                size = self.config.drone_size
            self.enemy_states.append({
                "type": etype, "x": float(ex), "y": float(ey),
                "hp": hp, "max_hp": hp, "active": True,
                "color": color, "size": size,
                "shoot_cd": 60, "direction": 1, "patrol_cd": 0,
                "base_y": float(ey), "start_col": ed["col"],
            })

        # Build pickups
        pickup_defs = _build_pickup_defs()
        self.pickup_states = []
        for pd in pickup_defs:
            ts = self.config.tile_size
            self.pickup_states.append({
                "x": float(pd["col"] * ts), "y": float(pd["row"] * ts),
                "active": True, "color": self.config.health_color,
                "size": self.config.health_size,
            })

        # Camera
        self.camera = Camera(
            position=Vector2D(self.player_x, self.player_y),
            mode=CameraMode.FOLLOW,
            lerp_factor=0.1,
        )

        self.scene.transition(SceneState.GAMEPLAY)

    def _parse_tiles(self):
        self.tile_solid = set()
        self.tile_platform = set()
        self.tile_finish = set()
        for y, row in enumerate(self.level_grid):
            for x, ch in enumerate(row):
                if ch == "#":
                    self.tile_solid.add((x, y))
                elif ch == "=":
                    self.tile_platform.add((x, y))
                elif ch == "F":
                    self.tile_finish.add((x, y))

    def _tile_at(self, col, row) -> str:
        if 0 <= row < len(self.level_grid) and 0 <= col < len(self.level_grid[0]):
            return self.level_grid[row][col]
        return "."

    def _collide_tile_solid(self, x, y, w, h) -> bool:
        """Check if rect overlaps any solid tile."""
        ts = self.config.tile_size
        c0 = int(x // ts)
        c1 = int((x + w - 1) // ts)
        r0 = int(y // ts)
        r1 = int((y + h - 1) // ts)
        for c in range(c0, c1 + 1):
            for r in range(r0, r1 + 1):
                if (c, r) in self.tile_solid:
                    return True
        return False

    def _collide_tile_platform_top(self, x, y, w, vy) -> bool:
        """One-way platform collision: only from above."""
        ts = self.config.tile_size
        c0 = int(x // ts)
        c1 = int((x + w - 1) // ts)
        r = int(y // ts)
        if vy >= 0 and (c0, r) in self.tile_platform or (c1, r) in self.tile_platform:
            return True
        return False

    def _on_finish(self, x, w) -> bool:
        ts = self.config.tile_size
        col = int((x + w / 2) // ts)
        for r in range(self.config.level_height):
            if (col, r) in self.tile_finish:
                return True
        return False

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
        elif self.scene.is_state(SceneState.GAMEPLAY):
            if event.key in (pygame.K_UP, pygame.K_w):
                if self.on_ground:
                    self.player_vy = self.config.jump_impulse
                    self.on_ground = False

    def update(self):
        if not self.scene.is_playing():
            return

        import pygame
        self.frame += 1
        self.params = self._get_params()

        # --- Player movement ---
        keys = pygame.key.get_pressed()
        speed = self.params.get("player_speed", self.config.player_speed)
        pw, ph = self.config.player_size

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += speed
            self.facing_right = True

        # Clamp left
        if self.player_x < 0:
            self.player_x = 0

        # Gravity
        self.player_vy += self.config.gravity
        self.player_y += self.player_vy

        # Solid tile collision (horizontal)
        if self._collide_tile_solid(self.player_x, self.player_y, pw, ph):
            # Push back
            ts = self.config.tile_size
            if self.facing_right:
                col = int((self.player_x + pw) // ts)
                self.player_x = col * ts - pw - 0.1
            else:
                col = int(self.player_x // ts)
                self.player_x = (col + 1) * ts + 0.1

        # Ground / platform collision (vertical)
        self.on_ground = False
        ts = self.config.tile_size

        # Check solid tiles below
        feet_row = int((self.player_y + ph) // ts)
        c0 = int(self.player_x // ts)
        c1 = int((self.player_x + pw - 1) // ts)
        for c in range(c0, c1 + 1):
            if (c, feet_row) in self.tile_solid:
                self.player_y = feet_row * ts - ph
                self.player_vy = 0
                self.on_ground = True
                break

        # Check one-way platforms (only from above)
        if not self.on_ground and self.player_vy >= 0:
            if self._collide_tile_platform_top(self.player_x, self.player_y + ph, pw, self.player_vy):
                feet_row_p = int((self.player_y + ph) // ts)
                self.player_y = feet_row_p * ts - ph
                self.player_vy = 0
                self.on_ground = True

        # Check solid tiles above (ceiling)
        head_row = int(self.player_y // ts)
        c0 = int(self.player_x // ts)
        c1 = int((self.player_x + pw - 1) // ts)
        for c in range(c0, c1 + 1):
            if (c, head_row) in self.tile_solid and self.player_vy < 0:
                self.player_y = (head_row + 1) * ts
                self.player_vy = 0

        # Fall death
        if self.player_y > self.config.level_height * ts + 100:
            self.player_hp = 0

        # --- Shooting ---
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if keys[pygame.K_SPACE] and self.shoot_cd <= 0:
            bspeed = self.params.get("player_bullet_speed", self.config.bullet_speed)
            bx = self.player_x + (pw if self.facing_right else -self.config.bullet_size[0])
            by = self.player_y + ph / 2 - self.config.bullet_size[1] / 2
            bvx = bspeed if self.facing_right else -bspeed
            self.bullets.append(Bullet(bx, by, bvx, 0, self.config.bullet_color, self.config.bullet_size, True))
            self.shoot_cd = self.config.shoot_cooldown

        # --- Update bullets ---
        for b in self.bullets:
            b.update()
            # Remove off-screen bullets
            level_w = self.config.level_width * ts
            if b.x < -50 or b.x > level_w + 50 or b.y < -50 or b.y > self.config.screen_height + 50:
                b.active = False
            # Player bullets vs solid tiles
            if b.is_player and self._collide_tile_solid(b.x, b.y, b.size[0], b.size[1]):
                b.active = False
        self.bullets = [b for b in self.bullets if b.active]

        # --- Update enemies ---
        espeed = self.params.get("enemy_speed", 2.5)
        shoot_rate = self.params.get("enemy_shoot_rate", 80)
        grace = self.params.get("grace_period", 120)

        for e in self.enemy_states:
            if not e["active"]:
                continue
            etype = e["type"]

            if etype == "soldier":
                # Simple patrol
                e["patrol_cd"] += 1
                if e["patrol_cd"] > 60:
                    e["direction"] *= -1
                    e["patrol_cd"] = 0
                e["x"] += espeed * e["direction"] * 0.5
                # Clamp to patrol range
                center_x = e["start_col"] * ts
                if abs(e["x"] - center_x) > ts * 3:
                    e["direction"] *= -1

            elif etype == "drone":
                # Sine wave movement
                e["x"] += espeed * 0.8
                e["y"] = e["base_y"] + math.sin(self.frame * 0.05) * 30

            # Enemy shooting
            e["shoot_cd"] -= 1
            if e["shoot_cd"] <= 0 and self.frame > grace:
                # Only shoot if player is roughly on screen
                dx = self.player_x - e["x"]
                if abs(dx) < self.config.screen_width:
                    e["shoot_cd"] = shoot_rate
                    bvx = self.config.bullet_speed * 0.6 if dx > 0 else -self.config.bullet_speed * 0.6
                    bx = e["x"] + e["size"][0] / 2
                    by = e["y"] + e["size"][1] / 2
                    self.bullets.append(Bullet(bx, by, bvx, 0, self.config.enemy_bullet_color,
                                               self.config.enemy_bullet_size, False))

        # --- Collision: player bullets vs enemies ---
        for b in self.bullets:
            if not b.active or not b.is_player:
                continue
            for e in self.enemy_states:
                if not e["active"]:
                    continue
                if self._rects_overlap(b.x, b.y, b.size[0], b.size[1],
                                       e["x"], e["y"], e["size"][0], e["size"][1]):
                    b.active = False
                    e["hp"] -= 1
                    if e["hp"] <= 0:
                        e["active"] = False
                        stype = e["type"]
                        pts = self.config.scoring.get(stype, 10)
                        self.score.add(pts)
                    break

        # --- Collision: enemy bullets vs player ---
        if self.frame > grace:
            for b in self.bullets:
                if not b.active or b.is_player:
                    continue
                if self._rects_overlap(b.x, b.y, b.size[0], b.size[1],
                                       self.player_x, self.player_y, pw, ph):
                    b.active = False
                    self.player_hp -= 1

        # --- Collision: player vs enemies ---
        if self.frame > grace:
            for e in self.enemy_states:
                if not e["active"]:
                    continue
                if self._rects_overlap(self.player_x, self.player_y, pw, ph,
                                       e["x"], e["y"], e["size"][0], e["size"][1]):
                    self.player_hp -= 1
                    e["active"] = False

        # --- Collision: player vs pickups ---
        for p in self.pickup_states:
            if not p["active"]:
                continue
            if self._rects_overlap(self.player_x, self.player_y, pw, ph,
                                   p["x"], p["y"], p["size"][0], p["size"][1]):
                p["active"] = False
                self.player_hp = min(self.player_hp + self.config.health_restore, 10)

        # --- Check win ---
        if self._on_finish(self.player_x, pw):
            self.won = True
            bonus = self.player_hp * self.config.scoring.get("health_bonus", 20)
            self.score.add(self.config.scoring.get("finish", 100) + bonus)
            self.score.update_best()
            self.scene.transition(SceneState.GAME_OVER)
            return

        # --- Check death ---
        if self.player_hp <= 0:
            self.score.update_best()
            self.scene.transition(SceneState.GAME_OVER)
            return

        # --- Update camera ---
        if self.camera is not None:
            target_pos = Vector2D(self.player_x + pw / 2, self.player_y + ph / 2)
            self.camera.position = self.camera.position.lerp(target_pos, self.camera.lerp_factor)
            # Clamp camera to level bounds
            half_w = self.config.screen_width / 2
            half_h = self.config.screen_height / 2
            level_w = self.config.level_width * ts
            self.camera.position.x = max(half_w, min(self.camera.position.x, level_w - half_w))
            self.camera.position.y = max(half_h, min(self.camera.position.y, self.config.level_height * ts - half_h))

    @staticmethod
    def _rects_overlap(x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
