"""Data types for the PyGame Studio MCP server."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ScreenSpec:
    width: int = 800
    height: int = 600
    fps: int = 60


@dataclass
class PlayerSpec:
    symbol: str = "@"
    hp: int | None = None
    speed: float | None = None
    attack: float | None = None
    color: list[int] | None = None


@dataclass
class EnemySpec:
    symbol: str = "E"
    speed: float | None = None
    spawn_rate: float | None = None
    hp: int | None = None
    count: int | None = None


@dataclass
class BulletSpec:
    symbol: str = "*"
    speed: float = 10.0


@dataclass
class ControlsSpec:
    move: str = "arrows"
    attack: str = "space"


@dataclass
class GameplaySpec:
    objective: str = ""
    duration: int = 0


@dataclass
class GameSpec:
    name: str = ""
    genre: Literal[
        "flappy", "shooter", "rogue", "fps", "topdown", "platformer"
    ] = "shooter"
    perspective: str | None = None
    screen: ScreenSpec | None = None
    player: PlayerSpec | None = None
    enemy: EnemySpec | None = None
    bullet: BulletSpec | None = None
    controls: ControlsSpec | None = None
    gameplay: GameplaySpec | None = None
    difficulty: dict[str, dict[str, float]] | None = None


@dataclass
class BuildResult:
    success: bool
    errors: str = ""
    parsed_errors: list[ParsedError] = field(default_factory=list)


@dataclass
class ParsedError:
    file: str
    line: int
    message: str
    severity: Literal["error", "warning"] = "error"


@dataclass
class ExecResult:
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool = False


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str


@dataclass
class CheckEnvironmentResult:
    ready: bool
    checks: list[CheckResult] = field(default_factory=list)
    fixes_applied: list[str] = field(default_factory=list)


# Genre-to-perspective mapping
PERSPECTIVE_MAP: dict[str, str] = {
    "flappy": "2d-plane",
    "shooter": "third-person",
    "rogue": "third-person",
    "fps": "first-person",
    "topdown": "top-down",
    "platformer": "2d-plane",
}

VALID_GENRES = list(PERSPECTIVE_MAP.keys())
