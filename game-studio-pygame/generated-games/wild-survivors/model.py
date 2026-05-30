"""Wild Survivors - 2D top-down cooperative survival game model."""
from __future__ import annotations

import math
import random
import sys

import pygame

from pygame_sdk import (
    Camera,
    CameraMode,
    CollisionPair,
    Entity,
    EntityStore,
    EntityType,
    MultiplayerManager,
    PlayerSlot,
    Rect,
    ScoreManager,
    SceneManager,
    SceneState,
    Vector2D,
    overlaps,
)

from config import WildSurvivorsConfig, load_config, DifficultyDef
from world_gen import generate_world

# Player colors for each slot
PLAYER_COLORS = [
    (255, 220, 50),   # yellow
    (80, 160, 255),   # blue
    (80, 220, 80),    # green
    (220, 80, 80),    # red
]

# Direction vectors for facing
DIR_VECTORS = {
    "up": Vector2D(0, -1),
    "down": Vector2D(0, 1),
    "left": Vector2D(-1, 0),
    "right": Vector2D(1, 0),
}


class PlayerState:
    """Runtime state for one player."""
    __slots__ = ("slot", "entity", "inventory", "facing", "alive", "attack_cd", "name")

    def __init__(self, slot: PlayerSlot, entity: Entity, name: str = "P1") -> None:
        self.slot = slot
        self.entity = entity
        self.inventory: dict[str, int] = {"wood": 0, "stone": 0, "iron": 0}
        self.facing: Vector2D = Vector2D(0, -1)
        self.alive: bool = True
        self.attack_cd: int = 0  # cooldown frames
        self.name = name


class EnemyState:
    """Runtime state for one enemy."""
    __slots__ = ("entity", "kind", "damage", "speed", "target_player")

    def __init__(self, entity: Entity, kind: str, damage: int, speed: float) -> None:
        self.entity = entity
        self.kind = kind
        self.damage = damage
        self.speed = speed
        self.target_player: PlayerState | None = None


class WildSurvivorsModel:
    """Main game model for Wild Survivors."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config: WildSurvivorsConfig = load_config(config_path)
        self.mp = MultiplayerManager(max_players=self.config.max_players)
        self.scene = SceneManager()
        self.score = ScoreManager()
        self.store = EntityStore()
        self.camera = Camera(mode=CameraMode.FOLLOW)
        self.tile_grid: list[list[int]] = []
        self.resources: list[Entity] = []
        self.enemies: list[EnemyState] = []
        self.structures: list[Entity] = []
        self.players: dict[str, PlayerState] = {}
        self.frame: int = 0
        self.difficulty_name: str = "normal"
        self.diff: DifficultyDef = self.config.difficulty.get("normal", DifficultyDef())
        self.grace_frames: int = 0
        self.spawn_timer: int = 0
        self.seed: int = 42

        # Detect multiplayer mode
        self._multiplayer_mode: bool = False

    def _detect_multiplayer(self) -> bool:
        """Check if running under game_stream_runner with multiplayer."""
        main_mod = sys.modules.get("__main__")
        if main_mod is None:
            return False
        pks = getattr(main_mod, "player_key_states", None)
        return pks is not None and len(pks) > 0

    def reset(self) -> None:
        """Generate a new world and reset all state."""
        self._multiplayer_mode = self._detect_multiplayer()
        self.frame = 0
        self.score.reset()
        self.store.clear()
        self.resources.clear()
        self.enemies.clear()
        self.structures.clear()
        self.players.clear()
        self.spawn_timer = 0

        self.seed = random.randint(1, 999999)
        ts = self.config.tile_size
        ww, wh = self.config.world_width, self.config.world_height

        # Generate world
        self.tile_grid, self.resources = generate_world(
            ww, wh, ts, self.config.resources, seed=self.seed,
        )
        for r in self.resources:
            self.store.add(r)

        # Difficulty
        self.grace_frames = self.diff.grace_period

        # Spawn center
        cx = (ww // 2) * ts
        cy = (wh // 2) * ts

        if self._multiplayer_mode:
            self._init_multiplayer_players(cx, cy, ts)
        else:
            self._init_single_player(cx, cy, ts)

        # Camera follows first player
        first = list(self.players.values())[0].entity
        world_pw = ww * ts
        world_ph = wh * ts
        self.camera = Camera(
            position=Vector2D(float(cx), float(cy)),
            mode=CameraMode.FOLLOW,
            target=first,
            bounds=Rect(0, 0, float(world_pw), float(world_ph)),
            lerp_factor=0.1,
        )

    def _init_single_player(self, cx: int, cy: int, ts: int) -> None:
        """Create one player for single-player mode."""
        slot = PlayerSlot("p0", "Player 1", PLAYER_COLORS[0])
        entity = Entity(
            type=EntityType.PLAYER,
            symbol="1",
            pos=Vector2D(float(cx), float(cy)),
            size=Vector2D(float(ts), float(ts)),
            hp=self.diff.player_hp,
            max_hp=self.diff.player_hp,
            color=PLAYER_COLORS[0],
        )
        self.store.add(entity)
        slot.entity = entity
        self.players["p0"] = PlayerState(slot, entity, "P1")

    def _init_multiplayer_players(self, cx: int, cy: int, ts: int) -> None:
        """Create player entities for multiplayer mode."""
        offsets = [
            Vector2D(-ts, 0),
            Vector2D(ts, 0),
            Vector2D(0, -ts),
            Vector2D(0, ts),
        ]
        pks = getattr(sys.modules.get("__main__"), "player_key_states", None)
        if pks is None:
            # Fallback to single player
            self._init_single_player(cx, cy, ts)
            return

        for i, pid in enumerate(pks.keys()):
            if i >= self.config.max_players:
                break
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            name = f"P{i + 1}"
            slot = self.mp.add_player(pid, name, color)
            off = offsets[i % len(offsets)]
            pos = Vector2D(float(cx) + off.x, float(cy) + off.y)
            entity = Entity(
                type=EntityType.PLAYER,
                symbol=str(i + 1),
                pos=pos,
                size=Vector2D(float(ts), float(ts)),
                hp=self.diff.player_hp,
                max_hp=self.diff.player_hp,
                color=color,
            )
            self.store.add(entity)
            slot.entity = entity
            self.players[pid] = PlayerState(slot, entity, name)

        if not self.players:
            self._init_single_player(cx, cy, ts)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events (single-player and menu)."""
        if event.type == pygame.KEYDOWN:
            if self.scene.is_state(SceneState.MENU):
                if event.key == pygame.K_RETURN:
                    self.scene.transition(SceneState.GAMEPLAY)
                    self.reset()
                elif event.key == pygame.K_1:
                    self.difficulty_name = "easy"
                    self.diff = self.config.difficulty.get("easy", DifficultyDef())
                elif event.key == pygame.K_2:
                    self.difficulty_name = "normal"
                    self.diff = self.config.difficulty.get("normal", DifficultyDef())
                elif event.key == pygame.K_3:
                    self.difficulty_name = "hard"
                    self.diff = self.config.difficulty.get("hard", DifficultyDef())

            elif self.scene.is_state(SceneState.GAME_OVER):
                if event.key == pygame.K_r:
                    self.scene.transition(SceneState.MENU)

    def update(self) -> None:
        """Main update tick."""
        if not self.scene.is_state(SceneState.GAMEPLAY):
            return

        self.frame += 1
        if self.grace_frames > 0:
            self.grace_frames -= 1

        # Update survival score every 60 frames (1 second)
        if self.frame % 60 == 0:
            self.score.add(1)

        # Read player inputs and process actions
        self._process_player_input()

        # Update enemies
        self._update_enemies()

        # Spawn enemies
        self._spawn_enemies()

        # Update camera
        self.camera.update()

        # Check game over
        all_dead = all(not p.alive for p in self.players.values())
        if all_dead:
            self.score.update_best()
            self.scene.transition(SceneState.GAME_OVER)

    def _process_player_input(self) -> None:
        """Read input for each player and apply movement/actions."""
        ts = self.config.tile_size
        ww, wh = self.config.world_width, self.config.world_height
        speed = self.config.player_speed

        pks = None
        if self._multiplayer_mode:
            pks = getattr(sys.modules.get("__main__"), "player_key_states", None)

        for pid, ps in self.players.items():
            if not ps.alive:
                continue

            if ps.attack_cd > 0:
                ps.attack_cd -= 1

            # Determine keys for this player
            if pks is not None and pid in pks:
                keys = pks[pid]
            else:
                keys = pygame.key.get_pressed()
                # In single player mode, keys is a sequence, not a dict
                # Convert to uniform interface
                keys = self._keys_sequence_to_dict(keys)

            # Movement
            dx, dy = 0.0, 0.0
            if self._key_down(keys, pygame.K_w) or self._key_down(keys, pygame.K_UP):
                dy -= 1
            if self._key_down(keys, pygame.K_s) or self._key_down(keys, pygame.K_DOWN):
                dy += 1
            if self._key_down(keys, pygame.K_a) or self._key_down(keys, pygame.K_LEFT):
                dx -= 1
            if self._key_down(keys, pygame.K_d) or self._key_down(keys, pygame.K_RIGHT):
                dx += 1

            # Update facing direction
            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
                ps.facing = Vector2D(dx, dy)

            # Apply movement with collision
            new_x = ps.entity.pos.x + dx * speed / 60.0
            new_y = ps.entity.pos.y + dy * speed / 60.0

            # Clamp to world bounds
            new_x = max(0, min(new_x, (ww - 1) * ts))
            new_y = max(0, min(new_y, (wh - 1) * ts))

            # Tile collision check
            tile_x = int(new_x // ts)
            tile_y = int(new_y // ts)
            if 0 <= tile_x < ww and 0 <= tile_y < wh:
                if self.tile_grid[tile_y][tile_x] == 0:
                    # Also check structure collision
                    if not self._collides_structure(new_x, new_y, ts):
                        ps.entity.pos.x = new_x
                        ps.entity.pos.y = new_y

            # Attack (space)
            if self._key_down(keys, pygame.K_SPACE) and ps.attack_cd == 0:
                self._player_attack(ps)
                ps.attack_cd = 15  # 0.25s cooldown

            # Build wall (E)
            if self._key_down(keys, pygame.K_e):
                self._player_build(ps, "wall")

            # Build campfire (R)
            if self._key_down(keys, pygame.K_r):
                self._player_build(ps, "campfire")

    def _keys_sequence_to_dict(self, keys) -> dict:
        """Convert pygame.key.get_pressed() result to a dict-like interface."""
        # keys is a pygame.key.ScancodeWrapper, indexable by key constant
        return _KeyWrapper(keys)

    def _key_down(self, keys, key: int) -> bool:
        """Check if a key is pressed, works with both dict and KeyWrapper."""
        if isinstance(keys, dict):
            return bool(keys.get(key, 0))
        try:
            return bool(keys[key])
        except (IndexError, KeyError):
            return False

    def _collides_structure(self, x: float, y: float, ts: int) -> bool:
        """Check if position collides with any structure."""
        for s in self.structures:
            if not s.active:
                continue
            if overlaps(
                Rect(x, y, float(ts), float(ts)),
                s.bounds(),
            ):
                return True
        return False

    def _player_attack(self, ps: PlayerState) -> None:
        """Player attacks adjacent tile in facing direction."""
        ts = self.config.tile_size
        attack_range = ts * 1.5
        attack_pos = ps.entity.pos.add(ps.facing.scale(ts))

        # Check enemies
        for es in self.enemies[:]:
            if not es.entity.active:
                continue
            dist = attack_pos.distance_to(es.entity.pos)
            if dist < attack_range:
                es.entity.hp -= 1
                if es.entity.hp <= 0:
                    es.entity.active = False
                    self.store.remove(es.entity.id)

        # Check resources
        for r in self.resources[:]:
            if not r.active:
                continue
            dist = attack_pos.distance_to(r.pos)
            if dist < attack_range:
                r.hp -= 1
                if r.hp <= 0:
                    drop = r.tags.get("drop", "wood")
                    ps.inventory[drop] = ps.inventory.get(drop, 0) + 1
                    r.active = False
                    self.store.remove(r.id)
                    # Clear tile grid
                    tx = int(r.pos.x // ts)
                    ty = int(r.pos.y // ts)
                    if (0 <= tx < self.config.world_width
                            and 0 <= ty < self.config.world_height):
                        self.tile_grid[ty][tx] = 0

    def _player_build(self, ps: PlayerState, kind: str) -> None:
        """Try to build a structure at the player's facing tile."""
        if kind not in self.config.structures:
            return

        sdef = self.config.structures[kind]
        ts = self.config.tile_size

        # Check cost
        if ps.inventory.get("wood", 0) < sdef.cost_wood:
            return
        if ps.inventory.get("stone", 0) < sdef.cost_stone:
            return

        # Target tile
        target_x = ps.entity.pos.x + ps.facing.x * ts
        target_y = ps.entity.pos.y + ps.facing.y * ts

        # Check tile is walkable and empty
        tx = int(target_x // ts)
        ty = int(target_y // ts)
        if not (0 <= tx < self.config.world_width and 0 <= ty < self.config.world_height):
            return
        if self.tile_grid[ty][tx] != 0:
            return
        if self._collides_structure(target_x, target_y, ts):
            return

        # Deduct cost
        ps.inventory["wood"] = ps.inventory.get("wood", 0) - sdef.cost_wood
        ps.inventory["stone"] = ps.inventory.get("stone", 0) - sdef.cost_stone

        # Place structure
        ent = Entity(
            type=EntityType.STRUCTURE,
            symbol="W" if kind == "wall" else "F",
            pos=Vector2D(target_x, target_y),
            size=Vector2D(float(ts), float(ts)),
            hp=sdef.hp,
            max_hp=sdef.hp,
            color=sdef.color,
            tags={"structure_type": kind},
        )
        self.store.add(ent)
        self.structures.append(ent)
        # Mark tile blocked
        self.tile_grid[ty][tx] = 1

    def _update_enemies(self) -> None:
        """Move enemies toward nearest alive player."""
        ts = self.config.tile_size
        alive_players = [p for p in self.players.values() if p.alive]
        if not alive_players:
            return

        for es in self.enemies[:]:
            if not es.entity.active:
                continue

            # Find nearest player
            nearest = None
            nearest_dist = float("inf")
            for p in alive_players:
                d = es.entity.pos.distance_to(p.entity.pos)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest = p

            if nearest is None:
                continue

            # Move toward player
            direction = nearest.entity.pos.sub(es.entity.pos).normalize()
            speed = es.speed / 60.0

            new_x = es.entity.pos.x + direction.x * speed
            new_y = es.entity.pos.y + direction.y * speed

            # Tile collision for enemies
            tx = int(new_x // ts)
            ty = int(new_y // ts)
            if (0 <= tx < self.config.world_width
                    and 0 <= ty < self.config.world_height
                    and self.tile_grid[ty][tx] == 0):
                if not self._collides_structure(new_x, new_y, ts):
                    es.entity.pos.x = new_x
                    es.entity.pos.y = new_y

            # Check collision with player
            for p in alive_players:
                if es.entity.pos.distance_to(p.entity.pos) < ts:
                    if self.grace_frames <= 0:
                        p.entity.hp -= es.damage
                        if p.entity.hp <= 0:
                            p.alive = False
                            p.entity.active = False
                            self.store.remove(p.entity.id)

            # Check collision with structures - enemies damage structures
            for s in self.structures:
                if not s.active:
                    continue
                if es.entity.pos.distance_to(s.pos) < ts:
                    s.hp -= 1
                    if s.hp <= 0:
                        s.active = False
                        self.store.remove(s.id)
                        stx = int(s.pos.x // ts)
                        sty = int(s.pos.y // ts)
                        if (0 <= stx < self.config.world_width
                                and 0 <= sty < self.config.world_height):
                            self.tile_grid[sty][stx] = 0

    def _spawn_enemies(self) -> None:
        """Spawn enemies at world edges on a timer."""
        if self.grace_frames > 0:
            return

        self.spawn_timer += 1
        rate = self.diff.spawn_rate
        if self.spawn_timer < rate:
            return

        self.spawn_timer = 0

        # Pick random edge
        ts = self.config.tile_size
        ww, wh = self.config.world_width, self.config.world_height
        side = random.randint(0, 3)
        if side == 0:  # top
            ex = random.randint(0, ww - 1) * ts
            ey = 0
        elif side == 1:  # bottom
            ex = random.randint(0, ww - 1) * ts
            ey = (wh - 1) * ts
        elif side == 2:  # left
            ex = 0
            ey = random.randint(0, wh - 1) * ts
        else:  # right
            ex = (ww - 1) * ts
            ey = random.randint(0, wh - 1) * ts

        # Check tile is walkable
        ttx = int(ex // ts)
        tty = int(ey // ts)
        if not (0 <= ttx < ww and 0 <= tty < wh):
            return
        if self.tile_grid[tty][ttx] != 0:
            return

        # Choose enemy type based on spawn rates
        roll = random.random()
        total_rate = sum(e.spawn_rate for e in self.config.enemies.values())
        cumulative = 0.0
        chosen = "slime"
        for ename, edef in self.config.enemies.items():
            cumulative += edef.spawn_rate / total_rate
            if roll <= cumulative:
                chosen = ename
                break

        edef = self.config.enemies.get(chosen)
        if edef is None:
            return

        ent = Entity(
            type=EntityType.ENEMY,
            symbol="s" if chosen == "slime" else "S",
            pos=Vector2D(float(ex), float(ey)),
            size=Vector2D(float(ts), float(ts)),
            hp=edef.hp,
            max_hp=edef.hp,
            color=edef.color,
        )
        self.store.add(ent)
        self.enemies.append(EnemyState(
            entity=ent,
            kind=chosen,
            damage=edef.damage,
            speed=edef.speed,
        ))


class _KeyWrapper:
    """Wraps pygame key sequence to support both index and dict access."""
    __slots__ = ("_keys",)

    def __init__(self, keys) -> None:
        self._keys = keys

    def __getitem__(self, key: int) -> int:
        return self._keys[key]

    def get(self, key: int, default: int = 0) -> int:
        try:
            return self._keys[key]
        except (IndexError, KeyError):
            return default
