"""Zombie FPS -- raycasting first-person zombie survival shooter.

WASD move, mouse aim, click to shoot. Survive 60 seconds in a
procedurally generated dungeon. Score = zombies killed x 100.
"""

import math
import random

import pygame

from pygame_sdk import (
    Entity, EntityType, EntityStore, Vector2D,
    Camera, CameraMode, RaycastRenderer, draw_minimap,
    DungeonConfig, generate_dungeon,
    SceneManager, SceneState, ScoreManager, TileMap,
    apply_velocity, apply_drag,
)

# -- constants ---------------------------------------------------------------
GAME_SECONDS = 60
MOUSE_SENS = 0.003
HIT_THRESH = 0.4
PLAYER_R = 0.25
ENEMY_R = 0.3
DRAG_COEFF = 0.03
STEER_STRENGTH = 0.12


class GameModel:
    """All game state, logic and rendering for Zombie FPS."""

    # -- initialisation -------------------------------------------------------
    def __init__(self, config):
        self.cfg = config
        self.difficulty = "normal"
        self.scene = SceneManager()
        self.scene.transition(SceneState.MENU)
        self.score = ScoreManager()
        self._init_world()

    def _diff(self):
        return self.cfg.get("difficulty", {}).get(self.difficulty, {})

    def _init_world(self):
        cfg = self.cfg
        diff = self._diff()

        dc = DungeonConfig(
            width=cfg["dungeon"]["width"],
            height=cfg["dungeon"]["height"],
            min_room_size=cfg["dungeon"]["min_room_size"],
            max_room_size=cfg["dungeon"]["max_room_size"],
            max_rooms=cfg["dungeon"]["max_rooms"],
            wall_color=tuple(cfg["dungeon"]["wall_color"]),
            floor_color=tuple(cfg["dungeon"]["floor_color"]),
            corridor_color=tuple(cfg["dungeon"]["corridor_color"]),
        )
        self.tilemap = generate_dungeon(dc)

        start = self._walkable_pos(0)
        php = diff.get("player_hp", cfg["player"]["hp"])
        self.player = Entity(
            type=EntityType.PLAYER,
            symbol=cfg["player"]["symbol"],
            pos=start,
            hp=php, max_hp=php,
            color=tuple(cfg["player"]["color"]),
        )

        self.cam = Camera.first_person_camera(position=start, direction=0.0)
        self.cam.fov_angle = math.pi / 3
        self.ray = RaycastRenderer(self.cam, self.tilemap)

        self.enemies = []

        fps = cfg["screen"]["fps"]
        self.grace = int(2.5 * fps)
        self.tick = 0
        self.max_tick = GAME_SECONDS * fps
        self.spawn_cd = 0
        self.fire_cd = 0
        self.flash_muzzle = 0
        self.flash_damage = 0
        self.flash_hit = 0
        self.damage_cd = 0

        for _ in range(diff.get("enemy_count", cfg["enemies"]["count"])):
            self._spawn(diff)

    # -- helpers --------------------------------------------------------------
    def _walkable_pos(self, min_dist):
        for _ in range(400):
            x = random.uniform(1.5, self.tilemap.width - 1.5)
            y = random.uniform(1.5, self.tilemap.height - 1.5)
            if not self.tilemap.is_walkable(int(x), int(y)):
                continue
            if min_dist > 0 and self.player:
                if Vector2D(x, y).distance_to(self.player.pos) < min_dist:
                    continue
            return Vector2D(x, y)
        return Vector2D(3.5, 3.5)

    def _spawn(self, diff=None):
        diff = diff or self._diff()
        e = self.cfg["enemies"]
        pos = self._walkable_pos(5.0)
        ehp = diff.get("enemy_hp", e["hp"])
        enemy = Entity(
            type=EntityType.ENEMY, symbol="Z", pos=pos,
            hp=ehp, max_hp=ehp, size=Vector2D(0.6, 0.6),
            color=tuple(e["color"]),
        )
        speed = diff.get("enemy_speed", e["speed"])
        self.enemies.append({"e": enemy, "speed": speed})

    def _pos_ok(self, x, y, radius=PLAYER_R):
        r = radius
        for dx in (-r, 0, r):
            for dy in (-r, 0, r):
                if not self.tilemap.is_walkable(int(x + dx), int(y + dy)):
                    return False
        return True

    def _slide_move(self, dx, dy):
        ox, oy = self.cam.position.x, self.cam.position.y
        nx, ny = ox + dx, oy + dy
        if self._pos_ok(nx, ny):
            self.cam.position = Vector2D(nx, ny)
        elif self._pos_ok(nx, oy):
            self.cam.position = Vector2D(nx, oy)
        elif self._pos_ok(ox, ny):
            self.cam.position = Vector2D(ox, ny)

    def _move_enemy_physics(self, rec, target_pos):
        """Physics-based enemy movement: steering force, inertia, wall bounce."""
        e = rec["e"]
        target_speed = rec["speed"]

        dx = target_pos.x - e.pos.x
        dy = target_pos.y - e.pos.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            return

        # desired velocity toward target
        desired_vx = dx / dist * target_speed
        desired_vy = dy / dist * target_speed

        # steering: gradually turn current vel toward desired
        steer_x = (desired_vx - e.vel.x) * STEER_STRENGTH
        steer_y = (desired_vy - e.vel.y) * STEER_STRENGTH
        e.vel = Vector2D(e.vel.x + steer_x, e.vel.y + steer_y)

        # clamp speed
        speed = math.sqrt(e.vel.x ** 2 + e.vel.y ** 2)
        max_spd = target_speed * 1.5
        if speed > max_spd:
            e.vel = Vector2D(e.vel.x / speed * max_spd, e.vel.y / speed * max_spd)

        # integrate position
        nx = e.pos.x + e.vel.x
        ny = e.pos.y + e.vel.y

        # wall collision with bounce
        can_x = self._pos_ok(nx, e.pos.y, ENEMY_R)
        can_y = self._pos_ok(e.pos.x, ny, ENEMY_R)
        can_xy = self._pos_ok(nx, ny, ENEMY_R)

        if can_xy:
            e.pos = Vector2D(nx, ny)
        elif can_x:
            e.pos = Vector2D(nx, e.pos.y)
            e.vel = Vector2D(e.vel.x, -e.vel.y * 0.3)
        elif can_y:
            e.pos = Vector2D(e.pos.x, ny)
            e.vel = Vector2D(-e.vel.x * 0.3, e.vel.y)
        else:
            e.vel = Vector2D(-e.vel.x * 0.3, -e.vel.y * 0.3)

        # friction
        apply_drag(e, DRAG_COEFF)

    # -- events ---------------------------------------------------------------
    def handle_event(self, ev):
        if self.scene.is_state(SceneState.MENU):
            self._ev_menu(ev)
        elif self.scene.is_state(SceneState.GAMEPLAY):
            self._ev_play(ev)
        elif self.scene.is_state(SceneState.GAME_OVER):
            self._ev_over(ev)

    def _ev_menu(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key == pygame.K_SPACE:
            self.scene.transition(SceneState.GAMEPLAY)
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
        elif ev.key == pygame.K_1:
            self.difficulty = "easy"
        elif ev.key == pygame.K_2:
            self.difficulty = "normal"
        elif ev.key == pygame.K_3:
            self.difficulty = "hard"

    def _ev_play(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.fire_cd <= 0:
                self._shoot()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)

    def _ev_over(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
            self.enemies.clear()
            self.score.reset()
            self._init_world()
            self.scene.transition(SceneState.MENU)

    # -- shooting (hitscan) ---------------------------------------------------
    def _shoot(self):
        self.fire_cd = self.cfg["player"]["fire_rate"]
        self.flash_muzzle = 4
        fwd = self.cam.forward()
        cp = self.cam.position
        wall_d = self.ray.cast_ray(self.cam.direction).distance

        best, best_d = None, wall_d
        for rec in self.enemies:
            e = rec["e"]
            if not e.active or e.hp <= 0:
                continue
            tx, ty = e.pos.x - cp.x, e.pos.y - cp.y
            along = tx * fwd.x + ty * fwd.y
            if along <= 0:
                continue
            perp = abs(tx * fwd.y - ty * fwd.x)
            if perp < HIT_THRESH and along < best_d:
                best, best_d = e, along

        if best is not None:
            best.hp -= self.cfg["player"]["weapon_damage"]
            self.flash_hit = 6
            # knockback -- push zombie away from player
            kb_dir = Vector2D(best.pos.x - cp.x, best.pos.y - cp.y)
            kb_len = math.sqrt(kb_dir.x ** 2 + kb_dir.y ** 2)
            if kb_len > 0.01:
                best.vel = Vector2D(
                    best.vel.x + kb_dir.x / kb_len * 0.15,
                    best.vel.y + kb_dir.y / kb_len * 0.15,
                )
            if best.hp <= 0:
                best.active = False
                self.score.add(100)

    # -- update ---------------------------------------------------------------
    def update(self):
        if not self.scene.is_state(SceneState.GAMEPLAY):
            return

        self.tick += 1

        if self.tick >= self.max_tick or self.player.hp <= 0:
            self._end()
            return

        grace_on = self.tick < self.grace

        # mouse look
        mdx, _ = pygame.mouse.get_rel()
        self.cam.direction += mdx * MOUSE_SENS

        # keyboard move
        keys = pygame.key.get_pressed()
        spd = self.cfg["player"]["speed"]
        f = self.cam.forward()
        r = self.cam.right()
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w]: dx += f.x * spd; dy += f.y * spd
        if keys[pygame.K_s]: dx -= f.x * spd; dy -= f.y * spd
        if keys[pygame.K_a]: dx -= r.x * spd; dy -= r.y * spd
        if keys[pygame.K_d]: dx += r.x * spd; dy += r.y * spd
        if dx or dy:
            self._slide_move(dx, dy)
        self.player.pos = Vector2D(self.cam.position.x, self.cam.position.y)

        # cooldowns
        if self.fire_cd > 0:      self.fire_cd -= 1
        if self.flash_muzzle > 0: self.flash_muzzle -= 1
        if self.flash_damage > 0: self.flash_damage -= 1
        if self.flash_hit > 0:    self.flash_hit -= 1
        if self.damage_cd > 0:    self.damage_cd -= 1

        # enemies -- physics-based chase
        ecfg = self.cfg["enemies"]
        for rec in self.enemies:
            e = rec["e"]
            if not e.active:
                continue
            dist = e.pos.distance_to(self.player.pos)
            if dist > ecfg["attack_range"]:
                self._move_enemy_physics(rec, self.player.pos)
            if not grace_on and self.damage_cd <= 0:
                if dist < ecfg["attack_range"]:
                    self.player.hp -= ecfg["damage"]
                    self.flash_damage = 10
                    self.damage_cd = 45

        self.enemies = [r for r in self.enemies if r["e"].active]

        # spawning
        diff = self._diff()
        self.spawn_cd += 1
        alive = len(self.enemies)
        mx = diff.get("max_alive", ecfg["max_alive"])
        iv = diff.get("spawn_interval", ecfg["spawn_interval"])
        if self.spawn_cd >= iv and alive < mx:
            self.spawn_cd = 0
            self._spawn(diff)

    def _end(self):
        self.scene.transition(SceneState.GAME_OVER)
        self.score.update_best()
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # -- rendering ------------------------------------------------------------
    def render(self, surf):
        if self.scene.is_state(SceneState.MENU):       self._draw_menu(surf)
        elif self.scene.is_state(SceneState.GAMEPLAY):  self._draw_play(surf)
        elif self.scene.is_state(SceneState.GAME_OVER): self._draw_over(surf)

    # -- menu -----------------------------------------------------------------
    def _draw_menu(self, s):
        w, h = s.get_size()
        s.fill((10, 10, 20))
        fb = pygame.font.Font(None, 74)
        fm = pygame.font.Font(None, 34)
        fs = pygame.font.Font(None, 26)

        t = fb.render("ZOMBIE FPS", True, (220, 50, 50))
        s.blit(t, (w // 2 - t.get_width() // 2, h // 5))

        t2 = fm.render("Survive 60 seconds in the dungeon!", True, (180, 180, 180))
        s.blit(t2, (w // 2 - t2.get_width() // 2, h // 5 + 80))

        for i, ln in enumerate(["WASD: Move | Mouse: Aim | Click: Shoot",
                                  "ESC: Release mouse"]):
            t3 = fs.render(ln, True, (110, 110, 110))
            s.blit(t3, (w // 2 - t3.get_width() // 2, h // 2 - 10 + i * 28))

        cols = {"easy": (100, 255, 100), "normal": (255, 255, 0), "hard": (255, 80, 80)}
        for i, (k, lab) in enumerate([("easy", "EASY"), ("normal", "NORMAL"), ("hard", "HARD")]):
            c = cols[k] if self.difficulty == k else (70, 70, 70)
            arrow = ">> " if self.difficulty == k else "   "
            td = fm.render(f"{arrow}[{i + 1}] {lab}", True, c)
            s.blit(td, (w // 2 - td.get_width() // 2, h * 2 // 3 - 20 + i * 36))

        ts = fm.render("[Press SPACE to start]", True, (255, 255, 0))
        s.blit(ts, (w // 2 - ts.get_width() // 2, h - 70))

    # -- gameplay -------------------------------------------------------------
    def _draw_play(self, s):
        w, h = s.get_size()

        # 3D raycast (walls, floor, ceiling)
        self.ray.render(s)

        # 3D cube enemy rendering
        self._draw_enemy_cubes(s, w, h)

        # damage flash
        if self.flash_damage > 0:
            ov = pygame.Surface((w, h), pygame.SRCALPHA)
            ov.fill((200, 0, 0, min(120, 120 * self.flash_damage // 10)))
            s.blit(ov, (0, 0))

        # hit flash on crosshair
        if self.flash_hit > 0:
            pygame.draw.circle(s, (255, 255, 200), (w // 2, h // 2), 16, 2)

        # muzzle flash
        if self.flash_muzzle > 0:
            fx, fy = w // 2 - 18, h - 80
            pygame.draw.ellipse(s, (255, 255, 200), (fx, fy, 36, 55))
            pygame.draw.ellipse(s, (255, 200, 50), (fx + 7, fy + 8, 22, 38))

        # weapon
        gx, gy = w // 2, h - 18
        pygame.draw.rect(s, (70, 70, 70), (gx - 5, gy - 72, 10, 72))
        pygame.draw.rect(s, (90, 90, 90), (gx - 4, gy - 70, 8, 68))
        pygame.draw.rect(s, (80, 60, 35), (gx - 10, gy - 14, 20, 30))
        pygame.draw.rect(s, (100, 75, 45), (gx - 8, gy - 12, 16, 26))

        # crosshair
        cx, cy = w // 2, h // 2
        for d in (-1, 1):
            pygame.draw.line(s, (0, 255, 0), (cx + 4 * d, cy), (cx + 13 * d, cy), 2)
            pygame.draw.line(s, (0, 255, 0), (cx, cy + 4 * d), (cx, cy + 13 * d), 2)

        # HUD
        self._draw_hud(s, w, h)

        # minimap
        draw_minimap(s, 10, 10, 130, 130, self.tilemap, self.player)

    def _project(self, wx, wy, cam_pos, cam_dir, half_fov, sw):
        """Project a world point to (screen_x, angle_off, dist). Returns None if behind."""
        dx = wx - cam_pos.x
        dy = wy - cam_pos.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            return None
        angle_to = math.atan2(dy, dx)
        angle_off = (angle_to - cam_dir + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_off) > half_fov + 0.3:
            return None
        sx = sw // 2 - int(angle_off / half_fov * (sw // 2))
        return sx, angle_off, dist

    def _draw_enemy_cubes(self, s, sw, sh):
        """Render enemies as true 3D cubes with corner projection and wall occlusion."""
        cam = self.cam
        cam_pos = cam.position
        cam_dir = cam.direction
        half_fov = cam.fov_angle / 2.0
        EYE_H = 0.5

        visible = []
        for rec in self.enemies:
            e = rec["e"]
            if not e.active or e.hp <= 0:
                continue
            dx = e.pos.x - cam_pos.x
            dy = e.pos.y - cam_pos.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 0.3:
                continue
            angle_to = math.atan2(dy, dx)
            angle_off = (angle_to - cam_dir + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_off) > half_fov + 0.3:
                continue
            # wall occlusion: cast ray toward zombie center
            wall_hit = self.ray.cast_ray(angle_to)
            if wall_hit.distance < dist - 0.4:
                continue
            visible.append((dist, e, angle_off))

        visible.sort(key=lambda v: -v[0])

        for dist, e, _ in visible:
            half = 0.3
            # 4 bottom corners of cube in world space
            corners_w = [
                (e.pos.x - half, e.pos.y - half),  # 0: near-left
                (e.pos.x + half, e.pos.y - half),  # 1: near-right
                (e.pos.x + half, e.pos.y + half),  # 2: far-right
                (e.pos.x - half, e.pos.y + half),  # 3: far-left
            ]

            # project each corner to screen
            projected = []
            for wx, wy in corners_w:
                p = self._project(wx, wy, cam_pos, cam_dir, half_fov, sw)
                if p is None:
                    projected.append(None)
                else:
                    projected.append(p)

            # skip if fewer than 2 corners visible
            vis_corners = [p for p in projected if p is not None]
            if len(vis_corners) < 2:
                continue

            # find leftmost and rightmost screen x for the cube
            all_sx = [p[0] for p in vis_corners]
            min_sx = min(all_sx)
            max_sx = max(all_sx)

            # cube height in pixels (cube is 0.6 world units tall)
            cube_h = max(4, int(0.6 / dist * sh))
            # floor level at this distance: sh//2 + sh//(2*dist) -- same as wall bottom
            floor_y = sh // 2 + int(float(sh) / dist * 0.5)
            cube_top_y = floor_y - cube_h
            cube_bot_y = floor_y

            if cube_h < 3:
                continue

            # clamp to screen
            min_sx = max(0, min_sx)
            max_sx = min(sw - 1, max_sx)
            cube_top_y = max(0, cube_top_y)
            cube_bot_y = min(sh, cube_bot_y)
            cube_w = max_sx - min_sx
            if cube_w < 2:
                continue

            # depth-based shading
            shade = max(0.25, min(1.0, 1.0 / (1.0 + dist * 0.1)))
            br, bg, bb = 180, 40, 40

            # Determine face visibility based on viewing angle relative to zombie
            view_angle = math.atan2(e.pos.y - cam_pos.y, e.pos.x - cam_pos.x)
            # relative angle in zombie's local frame
            rel = (view_angle + math.pi) % (2 * math.pi) - math.pi

            # -- draw the 3 visible faces --
            # side face offset (how much the side face sticks out)
            side_px = max(2, cube_w // 4)

            # determine which side face is visible
            show_left_side = math.sin(rel) > 0
            show_right_side = not show_left_side

            # -- SIDE FACE (darker) --
            side_shade = shade * 0.55
            side_color = (int(br * side_shade), int(bg * side_shade), int(bb * side_shade))
            side_border = (int(br * side_shade * 0.4), int(bg * side_shade * 0.4), int(bb * side_shade * 0.4))

            if show_left_side:
                # left side trapezoid
                side_pts = [
                    (min_sx, cube_top_y),
                    (min_sx + side_px, cube_top_y),
                    (min_sx + side_px, cube_bot_y),
                    (min_sx, cube_bot_y),
                ]
                front_left = min_sx + side_px
            else:
                side_pts = [
                    (max_sx - side_px, cube_top_y),
                    (max_sx, cube_top_y),
                    (max_sx, cube_bot_y),
                    (max_sx - side_px, cube_bot_y),
                ]
                front_left = min_sx
            pygame.draw.polygon(s, side_color, side_pts)
            pygame.draw.polygon(s, side_border, side_pts, 1)

            # -- FRONT FACE (main face, brightest) --
            front_right = max_sx - (side_px if show_right_side else 0)
            front_left = min_sx + (side_px if show_left_side else 0)
            front_w = front_right - front_left
            if front_w < 2:
                front_left = min_sx
                front_right = max_sx
                front_w = front_right - front_left

            front_color = (int(br * shade), int(bg * shade), int(bb * shade))
            front_border = (int(br * shade * 0.4), int(bg * shade * 0.4), int(bb * shade * 0.4))
            pygame.draw.rect(s, front_color, (front_left, cube_top_y, front_w, cube_h))
            pygame.draw.rect(s, front_border, (front_left, cube_top_y, front_w, cube_h), 1)

            # -- TOP FACE (lighter, parallelogram) --
            top_shade = min(1.0, shade * 1.35)
            top_color = (min(255, int(br * top_shade)), min(255, int(bg * top_shade)), min(255, int(bb * top_shade)))
            top_offset = max(1, cube_h // 6)

            if show_left_side:
                top_pts = [
                    (min_sx, cube_top_y),
                    (front_left, cube_top_y + top_offset),
                    (front_right, cube_top_y + top_offset),
                    (max_sx - side_px, cube_top_y),
                ]
            else:
                top_pts = [
                    (min_sx + side_px, cube_top_y),
                    (front_left, cube_top_y + top_offset),
                    (front_right, cube_top_y + top_offset),
                    (max_sx, cube_top_y),
                ]
            pygame.draw.polygon(s, top_color, top_pts)
            top_border = (int(br * top_shade * 0.5), int(bg * top_shade * 0.5), int(bb * top_shade * 0.5))
            pygame.draw.polygon(s, top_border, top_pts, 1)

            # -- face features on the front face --
            if front_w > 8 and cube_h > 15:
                eye_y = cube_top_y + top_offset + cube_h // 5
                eye_size = max(2, front_w // 10)
                el_x = front_left + front_w // 3
                er_x = front_left + front_w * 2 // 3
                pygame.draw.circle(s, (220, 220, 50), (el_x, eye_y), eye_size)
                pygame.draw.circle(s, (220, 220, 50), (er_x, eye_y), eye_size)
                pygame.draw.circle(s, (0, 0, 0), (el_x, eye_y), max(1, eye_size // 2))
                pygame.draw.circle(s, (0, 0, 0), (er_x, eye_y), max(1, eye_size // 2))

                if cube_h > 35:
                    mouth_y = cube_top_y + top_offset + cube_h * 3 // 5
                    mouth_w = front_w * 3 // 5
                    mouth_x = front_left + front_w // 2 - mouth_w // 2
                    pygame.draw.line(s, (255, 255, 255),
                                     (mouth_x, mouth_y),
                                     (mouth_x + mouth_w, mouth_y), max(1, front_w // 15))
                    for j in range(4):
                        tx = mouth_x + j * mouth_w // 4
                        pygame.draw.line(s, (255, 255, 255),
                                         (tx, mouth_y), (tx, mouth_y + cube_h // 15), max(1, front_w // 20))

            # "Z" label
            if front_w > 15 and cube_h > 40:
                z_font = pygame.font.Font(None, max(14, cube_h // 4))
                z_surf = z_font.render("Z", True, (255, 200, 200))
                zr = z_surf.get_rect(center=((front_left + front_right) // 2,
                                              (cube_top_y + cube_bot_y) // 2))
                s.blit(z_surf, zr)

            # hp bar above cube
            if cube_h > 10 and e.hp < e.max_hp:
                bar_w = max_sx - min_sx
                bar_h = max(2, cube_h // 15)
                bar_x = min_sx
                bar_y = cube_top_y - bar_h - 3
                pygame.draw.rect(s, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
                hp_w = int(bar_w * e.hp / e.max_hp)
                hp_color = (0, 200, 0) if e.hp > e.max_hp * 0.5 else (200, 200, 0)
                pygame.draw.rect(s, hp_color, (bar_x, bar_y, hp_w, bar_h))

    def _draw_hud(self, s, w, h):
        fn = pygame.font.Font(None, 28)
        fs = pygame.font.Font(None, 22)

        # HP bar
        hp, mhp = self.player.hp, self.player.max_hp
        bw, bh = 200, 22
        bx, by = w - bw - 15, h - 42
        pygame.draw.rect(s, (30, 30, 30), (bx, by, bw, bh))
        fw = int(bw * max(0, hp) / mhp)
        bc = (0, 200, 0) if hp > mhp * 0.5 else (200, 200, 0) if hp > mhp * 0.25 else (200, 0, 0)
        pygame.draw.rect(s, bc, (bx, by, fw, bh))
        pygame.draw.rect(s, (180, 180, 180), (bx, by, bw, bh), 2)
        s.blit(fn.render("HP {}/{}".format(hp, mhp), True, (255, 255, 255)), (bx + 6, by + 2))

        # score / kills
        kills = self.score.current // 100
        s.blit(fn.render("Score: {}".format(self.score.current), True, (255, 255, 0)), (w - 185, 10))
        s.blit(fs.render("Kills: {}".format(kills), True, (255, 150, 150)), (w - 185, 38))

        # timer
        fps = self.cfg["screen"]["fps"]
        rem = max(0.0, (self.max_tick - self.tick) / fps)
        tc = (255, 255, 255) if rem > 10 else (255, 50, 50)
        tt = fn.render("Time: {:.1f}s".format(rem), True, tc)
        s.blit(tt, (w // 2 - tt.get_width() // 2, 10))

        # grace
        if self.tick < self.grace:
            g = (self.grace - self.tick) / fps
            gt = fs.render("GRACE: {:.1f}s".format(g), True, (100, 255, 100))
            s.blit(gt, (w // 2 - gt.get_width() // 2, 38))

    # -- game over ------------------------------------------------------------
    def _draw_over(self, s):
        w, h = s.get_size()
        self.ray.render(s)
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        s.blit(ov, (0, 0))

        fb = pygame.font.Font(None, 66)
        fm = pygame.font.Font(None, 34)

        won = self.player.hp > 0
        t = fb.render("SURVIVED!" if won else "GAME OVER", True,
                       (0, 255, 0) if won else (255, 50, 50))
        s.blit(t, (w // 2 - t.get_width() // 2, h // 3 - 20))

        kills = self.score.current // 100
        for i, ln in enumerate(["Score: {}".format(self.score.current),
                                 "Kills: {}".format(kills),
                                 "Best: {}".format(self.score.best)]):
            r = fm.render(ln, True, (255, 255, 255))
            s.blit(r, (w // 2 - r.get_width() // 2, h // 2 + i * 42))

        hint = fm.render("[Press R to restart]", True, (255, 255, 0))
        s.blit(hint, (w // 2 - hint.get_width() // 2, h * 3 // 4))
