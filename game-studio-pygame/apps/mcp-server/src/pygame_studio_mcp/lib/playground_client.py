"""HTTP client for the Playground API."""

from __future__ import annotations

import os
from typing import Any

import httpx

PLAYGROUND_API_URL = os.environ.get(
    "PLAYGROUND_API_URL", "http://localhost:8080"
).rstrip("/")

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client (created lazily)."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=PLAYGROUND_API_URL,
            timeout=30.0,
        )
    return _client


async def close_client() -> None:
    """Close the shared client (for graceful shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


class PlaygroundError(Exception):
    """Raised when the Playground API returns an error."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Playground API error {status_code}: {detail}")


def _parse_error_detail(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        return data.get("detail", resp.text)
    except Exception:
        return resp.text


async def api_get(path: str, params: dict | None = None) -> Any:
    """GET from Playground API."""
    client = get_client()
    resp = await client.get(path, params=params)
    if resp.status_code >= 400:
        raise PlaygroundError(resp.status_code, _parse_error_detail(resp))
    return resp.json()


async def api_post_multipart(
    path: str,
    files: dict,
    data: dict,
) -> Any:
    """POST multipart form to Playground API."""
    client = get_client()
    resp = await client.post(path, files=files, data=data)
    if resp.status_code >= 400:
        raise PlaygroundError(resp.status_code, _parse_error_detail(resp))
    return resp.json()


async def api_download_zip(path: str) -> bytes:
    """GET a ZIP file from Playground API. Returns raw bytes."""
    client = get_client()
    resp = await client.get(path)
    if resp.status_code >= 400:
        raise PlaygroundError(resp.status_code, _parse_error_detail(resp))
    return resp.content


async def api_delete(path: str) -> None:
    """DELETE from Playground API."""
    client = get_client()
    resp = await client.delete(path)
    if resp.status_code >= 400 and resp.status_code != 204:
        raise PlaygroundError(resp.status_code, _parse_error_detail(resp))
