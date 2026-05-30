"""List games available on the Playground web platform."""

from __future__ import annotations

import httpx

from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_get,
)


async def list_playground_games(
    genre: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    order: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict:
    """Query games from Playground API."""
    params: dict = {}
    if genre is not None:
        params["genre"] = genre
    if search is not None:
        params["search"] = search
    if sort is not None:
        params["sort"] = sort
    if order is not None:
        params["order"] = order
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset

    try:
        games = await api_get("/api/games", params=params or None)
        return {"success": True, "games": games, "count": len(games)}
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
