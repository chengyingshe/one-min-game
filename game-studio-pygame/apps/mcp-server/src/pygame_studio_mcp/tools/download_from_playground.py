"""Download a game from Playground and extract it locally."""

from __future__ import annotations

import zipfile
from io import BytesIO

import httpx

from pygame_studio_mcp.lib.paths import project_dir
from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_download_zip,
)


async def download_from_playground(
    name: str,
    project: str | None = None,
) -> dict:
    """Download a game from Playground and extract it as a local project."""
    local_name = project or name
    dir_path = project_dir(local_name)

    try:
        zip_bytes = await api_download_zip(f"/api/games/{name}/download")
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

    # Extract ZIP
    dir_path.mkdir(parents=True, exist_ok=True)
    files_extracted = 0

    try:
        buf = BytesIO(zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            entries = zf.namelist()

            # Strip single top-level directory if present
            top_dirs = {n.split("/")[0] for n in entries if "/" in n}
            has_root_file = any("/" not in n for n in entries)
            strip_prefix = ""
            if len(top_dirs) == 1 and not has_root_file:
                strip_prefix = list(top_dirs)[0] + "/"

            for entry in entries:
                if entry == strip_prefix:
                    continue
                target = dir_path / entry[len(strip_prefix):]
                if entry.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(entry))
                    files_extracted += 1
    except zipfile.BadZipFile:
        return {"success": False, "error": "Downloaded file is not a valid ZIP"}

    return {
        "success": True,
        "path": str(dir_path),
        "files_extracted": files_extracted,
    }
