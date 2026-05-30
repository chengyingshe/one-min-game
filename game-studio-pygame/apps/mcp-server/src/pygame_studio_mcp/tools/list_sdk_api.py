"""Return the full PyGame SDK API surface for code generation reference."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

from pygame_studio_mcp.lib.paths import sdk_api_file


def _extract_api_from_source(source: str) -> dict[str, Any]:
    """Parse Python source to extract classes, functions, and constants."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    api: dict[str, Any] = {"types": {}, "functions": [], "constants": []}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods: list[str] = []
            fields: dict[str, str] = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    sig_parts = [arg.arg for arg in item.args.args if arg.arg != "self"]
                    methods.append(f"{item.name}({', '.join(sig_parts)})")
                elif isinstance(item, ast.AnnAssign) and item.target:
                    name = item.target.id if isinstance(item.target, ast.Name) else ""
                    if name:
                        fields[name] = ast.dump(item.annotation) if item.annotation else "Any"
            api["types"][node.name] = {
                "kind": "class",
                "fields": fields,
                "methods": methods,
            }
        elif isinstance(node, ast.FunctionDef):
            api["functions"].append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    api["constants"].append(target.id)

    return api


def get_sdk_api() -> dict[str, Any]:
    """Return the PyGame SDK API documentation."""
    api_file = sdk_api_file()

    # Try reading the actual SDK source for live API extraction
    if api_file.exists():
        source = api_file.read_text(encoding="utf-8")
        live_api = _extract_api_from_source(source)
        if live_api.get("types") or live_api.get("functions"):
            return live_api

    # Fallback: return documented API surface
    return {
        "types": {
            "Entity": {
                "kind": "class",
                "fields": {
                    "id": "int",
                    "type": "str",
                    "x": "float",
                    "y": "float",
                    "vx": "float",
                    "vy": "float",
                    "width": "float",
                    "height": "float",
                    "hp": "int",
                    "max_hp": "int",
                    "active": "bool",
                    "color": "tuple[int, int, int]",
                    "symbol": "str",
                },
                "methods": [
                    "rect()",
                    "center()",
                    "distance_to(other)",
                    "angle_to(other)",
                    "is_alive()",
                    "take_damage(amount)",
                    "heal(amount)",
                    "kill()",
                ],
            },
            "EntityStore": {
                "kind": "class",
                "methods": [
                    "add(entity)",
                    "remove(entity_id)",
                    "get(entity_id)",
                    "get_by_type(entity_type)",
                    "get_active()",
                    "update_all(fn)",
                    "count()",
                    "count_by_type(entity_type)",
                    "clear()",
                ],
            },
            "Vector2D": {
                "kind": "class",
                "fields": {"x": "float", "y": "float"},
                "methods": [
                    "add(other)",
                    "sub(other)",
                    "scale(s)",
                    "length()",
                    "normalize()",
                    "distance_to(other)",
                    "dot(other)",
                    "angle()",
                    "lerp(other, t)",
                    "rotate(angle)",
                ],
            },
            "Buffer": {
                "kind": "class",
                "methods": [
                    "fill(color)",
                    "draw_rect(rect, color, width=0)",
                    "draw_text(text, x, y, color, font=None)",
                    "draw_entity(entity)",
                    "draw_entities(entities)",
                    "draw_overlay(x, y, content, color)",
                    "blit(surface, pos)",
                ],
            },
            "SceneManager": {
                "kind": "class",
                "methods": [
                    "transition(state)",
                    "is(state)",
                    "is_playing()",
                    "toggle_pause()",
                    "current()",
                ],
            },
            "ScoreManager": {
                "kind": "class",
                "fields": {"current": "int", "best": "int"},
                "methods": [
                    "add(points)",
                    "reset()",
                    "update_best()",
                ],
            },
            "Camera": {
                "kind": "class",
                "fields": {
                    "x": "float",
                    "y": "float",
                    "target": "Entity | None",
                    "lerp_factor": "float",
                    "bounds": "Rect | None",
                },
                "methods": [
                    "follow(target)",
                    "update()",
                    "world_to_screen(wx, wy)",
                    "screen_to_world(sx, sy)",
                    "move(dx, dy)",
                ],
            },
            "TileMap": {
                "kind": "class",
                "methods": [
                    "get(x, y)",
                    "set(x, y, tile_type)",
                    "is_walkable(x, y)",
                    "is_solid(x, y)",
                    "load_from_strings(lines, legend)",
                    "render(surface, camera, tile_size)",
                ],
            },
            "AIAgent": {
                "kind": "class",
                "fields": {
                    "behavior": "str",
                    "chase_range": "float",
                    "attack_range": "float",
                    "speed": "float",
                },
                "methods": [
                    "update(tilemap, player, frame)",
                ],
            },
            "SceneState": {
                "kind": "enum",
                "values": ["MENU", "GAMEPLAY", "PAUSED", "GAME_OVER"],
            },
            "GameConfig": {
                "kind": "class",
                "fields": {
                    "name": "str",
                    "genre": "str",
                    "screen": "dict",
                    "player": "dict",
                    "difficulty": "dict",
                },
            },
        },
        "functions": [
            "apply_gravity(entity, gravity)",
            "apply_velocity(entity)",
            "apply_drag(entity, coefficient)",
            "set_velocity(entity, vx, vy)",
            "clamp_position(entity, min_x, min_y, max_x, max_y)",
            "overlaps(rect_a, rect_b)",
            "hit_bounds(entity, width, height)",
            "hit_ground(entity, height)",
            "check_collision_pairs(entities)",
            "resolve_collision(pair)",
            "bounce_velocity(vel, normal, restitution)",
            "generate_dungeon(config, rng)",
            "default_dungeon_config()",
            "default_game_config()",
            "load_config(path)",
            "draw_minimap(surface, x, y, w, h, tilemap, player)",
        ],
        "constants": [
            "SCENE_MENU",
            "SCENE_GAMEPLAY",
            "SCENE_PAUSED",
            "SCENE_GAME_OVER",
            "ENTITY_PLAYER",
            "ENTITY_ENEMY",
            "ENTITY_BULLET",
            "ENTITY_OBSTACLE",
            "ENTITY_COLLECTIBLE",
            "DEFAULT_SCREEN_WIDTH",
            "DEFAULT_SCREEN_HEIGHT",
            "DEFAULT_FPS",
            "GRACE_PERIOD_SECONDS",
        ],
    }


async def list_sdk_api() -> dict[str, Any]:
    """Return the SDK API documentation."""
    return get_sdk_api()
