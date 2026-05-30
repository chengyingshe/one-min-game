"""Delete a game from the Playground web platform."""

from __future__ import annotations

import httpx

from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_delete,
)


async def delete_playground_game(name: str) -> dict:
    """Delete a game from the Playground."""
    try:
        await api_delete(f"/api/games/{name}")
        return {"success": True, "deleted": name}
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
