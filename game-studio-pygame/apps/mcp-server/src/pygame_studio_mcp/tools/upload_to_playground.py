"""Package a local game project as ZIP and upload to Playground."""

from __future__ import annotations

import io
import re
import zipfile

import yaml

from pygame_studio_mcp.lib.paths import project_dir
from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_post_multipart,
)
from pygame_studio_mcp.tools.capture_screenshot import capture_screenshot_base64

import httpx

_PROJECT_RE = re.compile(r"^[a-zA-Z0-9\-]+$")

_EXCLUDED_NAMES = {"__pycache__", "bin", ".git", "node_modules", ".venv"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}


def _zip_project(dir_path) -> bytes:
    """Create an in-memory ZIP of the project directory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(dir_path.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.name in _EXCLUDED_NAMES:
                continue
            if any(part in _EXCLUDED_NAMES for part in file_path.relative_to(dir_path).parts):
                continue
            if file_path.suffix in _EXCLUDED_SUFFIXES:
                continue
            arcname = str(file_path.relative_to(dir_path))
            zf.write(file_path, arcname)
    return buf.getvalue()


async def upload_to_playground(
    project: str,
    display_name: str | None = None,
    description: str | None = None,
    author_name: str | None = None,
) -> dict:
    """Package local game as ZIP and upload to Playground."""
    if not _PROJECT_RE.match(project):
        return {"success": False, "error": f"Invalid project name: {project}"}

    dir_path = project_dir(project)
    if not dir_path.exists():
        return {"success": False, "error": f"Project not found: {project}"}
    if not (dir_path / "main.py").exists():
        return {"success": False, "error": f"main.py not found in project: {project}"}

    # Read config.yaml for metadata defaults
    config_path = dir_path / "config.yaml"
    config: dict = {}
    if config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except Exception:
            config = {}

    genre = config.get("genre", "arcade")
    screen = config.get("screen", {}) or {}
    screen_width = screen.get("width", 800)
    screen_height = screen.get("height", 600)
    controls = config.get("controls", "")

    # Read config_yaml content for upload
    config_yaml = ""
    if config_path.exists():
        config_yaml = config_path.read_text(encoding="utf-8")

    # Create ZIP
    try:
        zip_bytes = _zip_project(dir_path)
    except Exception as exc:
        return {"success": False, "error": f"Failed to create ZIP: {exc}"}

    # Capture screenshot for preview image
    screenshot_b64 = await capture_screenshot_base64(project)

    # Build form data
    form_data: dict[str, str] = {
        "name": project,
        "display_name": display_name or config.get("name", project),
        "description": description or config.get("description", ""),
        "genre": str(genre),
        "author_name": author_name or "",
        "config_yaml": config_yaml,
        "screen_width": str(screen_width),
        "screen_height": str(screen_height),
        "controls": str(controls),
    }
    if screenshot_b64:
        form_data["screenshot_base64"] = screenshot_b64

    try:
        result = await api_post_multipart(
            "/api/upload",
            files={"file": (f"{project}.zip", zip_bytes, "application/zip")},
            data=form_data,
        )
        result["playground_url"] = f"{PLAYGROUND_API_URL}/play/{project}"
        return result
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
