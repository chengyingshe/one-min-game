"""Get detailed info about a specific game on the Playground."""

from __future__ import annotations

import httpx

from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_get,
)


async def get_playground_game(name: str) -> dict:
    """Get details of a specific Playground game."""
    try:
        game = await api_get(f"/api/games/{name}")
        return {"success": True, "game": game}
    except PlaygroundError as e:
        return {"success": False, "error": f"Playground API error {e.status_code}: {e.detail}"}
    except httpx.ConnectError:
        return {
            "success": False,
            "error": f"Cannot connect to Playground API at {PLAYGROUND_API_URL}. "
            "Start it with: make playground-up",
        }
    except httpx.TimeoutException:
        return {"success": False, "error": "Playground API request timed out"}
