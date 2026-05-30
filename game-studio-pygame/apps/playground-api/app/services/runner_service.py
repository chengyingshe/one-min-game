from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Optional

import docker
from docker.errors import ImageNotFound, APIError

from app.config import settings


def get_docker_client() -> docker.DockerClient:
    return docker.from_env()


def ensure_runner_image() -> None:
    client = get_docker_client()
    try:
        client.images.get(settings.RUNNER_IMAGE)
    except ImageNotFound:
        client.images.build(
            path=str(Path(__file__).resolve().parents[3] / "docker" / "game-runner"),
            tag=settings.RUNNER_IMAGE,
            rm=True,
        )


def run_game(
    game_name: str,
    duration_seconds: int = 10,
    capture_frames: Optional[list[int]] = None,
) -> dict:
    if capture_frames is None:
        capture_frames = [30, 60, 90, 120]

    client = get_docker_client()
    game_dir = Path(settings.GAMES_DIR) / game_name
    if not game_dir.exists():
        raise FileNotFoundError(f"Game source not found: {game_dir}")

    task_id = uuid.uuid4().hex[:12]
    output_dir = Path(settings.SCREENSHOTS_DIR) / game_name / task_id
    output_dir.mkdir(parents=True, exist_ok=True)

    run_config = {
        "capture_frames": capture_frames,
        "duration_seconds": duration_seconds,
        "output_dir": "/output",
    }

    start_ms = int(time.time() * 1000)

    try:
        volumes: dict = {
            "game-studios-pygame_game-data": {"bind": "/data", "mode": "rw"},
        }
        # Output dir inside the container must match the volume mount
        run_config["output_dir"] = f"/data/screenshots/{game_name}/{task_id}"
        container = client.containers.run(
            image=settings.RUNNER_IMAGE,
            command=[json.dumps(run_config)],
            volumes=volumes,
            working_dir="/game",
            environment={"GAME_DIR": f"/data/games/{game_name}"},
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            network_mode="none",
            detach=True,
            remove=False,
            stdout=True,
            stderr=True,
        )
        result = container.wait(timeout=duration_seconds + 30)
        exit_code = result.get("StatusCode", -1)
        stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
        stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
        container.remove()
    except Exception as e:
        exit_code = -1
        stdout = ""
        stderr = str(e)

    duration_ms = int(time.time() * 1000) - start_ms

    screenshots: list[str] = []
    gif_url: Optional[str] = None

    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for frame in manifest.get("frames", []):
            filename = frame.get("filename", "")
            if filename:
                screenshots.append(f"/static/screenshots/{game_name}/{task_id}/{filename}")
        gif_url = manifest.get("gif_url")
        if gif_url:
            gif_url = f"/static/screenshots/{game_name}/{task_id}/{gif_url}"

    return {
        "screenshots": screenshots,
        "gif_url": gif_url,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "stdout": stdout,
        "stderr": stderr,
        "task_id": task_id,
    }
