"""PyGame Runtime SDK - Python port of the BubbleTea game engine SDK.

Provides entity management, physics, collision, rendering, scene management,
scoring, input mapping, camera, raycasting, pathfinding, AI, and more
for building mini-games with PyGame.
"""

# Core types
from .vector import Vector2D

# Entity system
from .entity import Color, Entity, EntityStore, EntityType

# Physics
from .physics import (
    apply_gravity,
    apply_velocity,
    clamp_position,
    set_velocity,
    set_velocity_y,
)

# Collision
from .collision import (
    CollisionPair,
    Rect,
    bounce_velocity,
    check_collision_pairs,
    check_layered_collisions,
    hit_bounds,
    hit_ground,
    overlaps,
    resolve_collision,
    separate_entities,
    slide_velocity,
)

# Rendering
from .renderer import Renderer

# Screenshot
from .screenshot import capture_screenshot

# Scene management
from .scene import SceneManager, SceneState

# Scoring
from .score import ScoreManager

# Timing
from .tick import TickScheduler

# Input
from .input import InputAction, InputMapper

# Configuration
from .config import (
    ControlsConfig,
    GameConfig,
    GameplayConfig,
    MultiplayerConfig,
    PlayerConfig,
    ScreenConfig,
    default_game_config,
    load_config,
    load_config_from_string,
)

# Difficulty
from .difficulty import DifficultyParams, DifficultyTier

# Material
from .material import (
    ICE_MATERIAL,
    RUBBER_MATERIAL,
    STATIC_MATERIAL,
    BOUNCY_MATERIAL,
    HEAVY_MATERIAL,
    PhysicsMaterial,
    default_material,
)

# Force
from .force import Force, ForceAccumulator, apply_drag, apply_gravity_2d

# Movement patterns
from .patterns import (
    GridPattern,
    HomingPattern,
    LinearPattern,
    MovementPattern,
    OrbitPattern,
    PatrolPattern,
    SinusoidalPattern,
    update_pattern,
)

# World / Tiles
from .world import TileMap, TileType

# Dungeon generation
from .dungeon import DungeonConfig, generate_dungeon

# Spatial hashing
from .spatial import SpatialHash

# Pathfinding
from .pathfind import PathFinder

# Camera
from .camera import Camera, CameraMode

# Raycasting
from .raycast import RayHit, RaycastRenderer, draw_minimap

# AI
from .ai import AIAgent, BehaviorType

# Multiplayer
from .multiplayer import MultiplayerManager, PlayerSlot

# LLM
from .llm import ask_llm, ask_llm_messages

# Styles / Colors
from . import styles

__all__ = [
    # Vector
    "Vector2D",
    # Entity
    "Color",
    "Entity",
    "EntityStore",
    "EntityType",
    # Physics
    "apply_gravity",
    "apply_velocity",
    "clamp_position",
    "set_velocity",
    "set_velocity_y",
    # Collision
    "CollisionPair",
    "Rect",
    "bounce_velocity",
    "check_collision_pairs",
    "check_layered_collisions",
    "hit_bounds",
    "hit_ground",
    "overlaps",
    "resolve_collision",
    "separate_entities",
    "slide_velocity",
    # Renderer
    "Renderer",
    # Screenshot
    "capture_screenshot",
    # Scene
    "SceneManager",
    "SceneState",
    # Score
    "ScoreManager",
    # Tick
    "TickScheduler",
    # Input
    "InputAction",
    "InputMapper",
    # Config
    "ControlsConfig",
    "GameConfig",
    "GameplayConfig",
    "MultiplayerConfig",
    "PlayerConfig",
    "ScreenConfig",
    "default_game_config",
    "load_config",
    "load_config_from_string",
    # Difficulty
    "DifficultyParams",
    "DifficultyTier",
    # Material
    "ICE_MATERIAL",
    "RUBBER_MATERIAL",
    "STATIC_MATERIAL",
    "BOUNCY_MATERIAL",
    "HEAVY_MATERIAL",
    "PhysicsMaterial",
    "default_material",
    # Force
    "Force",
    "ForceAccumulator",
    "apply_drag",
    "apply_gravity_2d",
    # Patterns
    "GridPattern",
    "HomingPattern",
    "LinearPattern",
    "MovementPattern",
    "OrbitPattern",
    "PatrolPattern",
    "SinusoidalPattern",
    "update_pattern",
    # World
    "TileMap",
    "TileType",
    # Dungeon
    "DungeonConfig",
    "generate_dungeon",
    # Spatial
    "SpatialHash",
    # Pathfinding
    "PathFinder",
    # Camera
    "Camera",
    "CameraMode",
    # Raycast
    "RayHit",
    "RaycastRenderer",
    "draw_minimap",
    # AI
    "AIAgent",
    "BehaviorType",
    # Multiplayer
    "MultiplayerManager",
    "MultiplayerConfig",
    "PlayerSlot",
    # LLM
    "ask_llm",
    "ask_llm_messages",
    # Styles module
    "styles",
]
