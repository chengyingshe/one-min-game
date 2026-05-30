"""Check if the development environment meets all requirements."""

from __future__ import annotations

from pathlib import Path

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.paths import get_studio_root, runtime_dir, sdk_dir
from pygame_studio_mcp.types import CheckEnvironmentResult, CheckResult


def _parse_version(output: str) -> tuple[int, int, int] | None:
    import re

    m = re.search(r"(\d+)\.(\d+)\.(\d+)", output)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _gte(v: tuple[int, int, int], minimum: tuple[int, int, int]) -> bool:
    return v > minimum or v == minimum


async def check_environment(auto_fix: bool = False) -> dict:
    """Check Python, PyGame, PyYAML, and project structure."""
    root = get_studio_root()
    checks: list[dict] = []
    fixes: list[str] = []

    # 1. Python
    py_result = run(["python3", "--version"], timeout=10)
    if py_result.returncode == 0:
        v = _parse_version(py_result.stdout)
        py_min = (3, 11, 0)
        if v and _gte(v, py_min):
            checks.append(
                {"name": "python", "passed": True, "message": f"Python {'.'.join(map(str, v))} detected"}
            )
        else:
            checks.append(
                {"name": "python", "passed": False, "message": f"Python >= 3.11.0 required, got: {py_result.stdout.strip()}"}
            )
    else:
        checks.append({"name": "python", "passed": False, "message": "Python 3 not found. Install Python 3.11+."})

    # 2. pip
    pip_result = run(["pip3", "--version"], timeout=10)
    if pip_result.returncode == 0:
        checks.append({"name": "pip", "passed": True, "message": f"pip detected: {pip_result.stdout.strip()}"})
    else:
        checks.append({"name": "pip", "passed": False, "message": "pip not found."})

    # 3. PyGame
    pg_result = run(
        ["python3", "-c", "import pygame; print(pygame.version.ver)"], timeout=10
    )
    if pg_result.returncode == 0:
        v = _parse_version(pg_result.stdout)
        pg_min = (2, 5, 0)
        if v and _gte(v, pg_min):
            checks.append(
                {"name": "pygame", "passed": True, "message": f"PyGame {'.'.join(map(str, v))} detected"}
            )
        else:
            checks.append(
                {"name": "pygame", "passed": False, "message": f"PyGame >= 2.5.0 required, got: {pg_result.stdout.strip()}"}
            )
    else:
        checks.append({"name": "pygame", "passed": False, "message": "PyGame not installed. Run: pip install pygame"})

    # 4. PyYAML
    yaml_result = run(
        ["python3", "-c", "import yaml; print(yaml.__version__)"], timeout=10
    )
    if yaml_result.returncode == 0:
        checks.append({"name": "pyyaml", "passed": True, "message": f"PyYAML {yaml_result.stdout.strip()} detected"})
    else:
        checks.append({"name": "pyyaml", "passed": False, "message": "PyYAML not installed. Run: pip install pyyaml"})

    # 5. MCP SDK
    mcp_result = run(
        ["python3", "-c", "import mcp; print(mcp.__version__)"], timeout=10
    )
    if mcp_result.returncode == 0:
        checks.append({"name": "mcp", "passed": True, "message": f"mcp {mcp_result.stdout.strip()} detected"})
    else:
        checks.append({"name": "mcp", "passed": False, "message": "mcp not installed. Run: pip install mcp"})

    # 6. SDK directory
    sdk_path = sdk_dir()
    sdk_init = sdk_path / "pygame_sdk" / "__init__.py"
    sdk_exists = sdk_init.exists()
    checks.append({
        "name": "pygame_sdk",
        "passed": sdk_exists,
        "message": "pygame_sdk found" if sdk_exists else "pygame_sdk not found at runtime/pygame-sdk/",
    })

    # 7. Templates directory
    from pygame_studio_mcp.lib.paths import templates_dir
    tdir = templates_dir()
    checks.append({
        "name": "templates",
        "passed": tdir.exists(),
        "message": "Templates directory found" if tdir.exists() else "Templates directory not found",
    })

    # 8. generated-games directory
    from pygame_studio_mcp.lib.paths import generated_games_dir
    gdir = generated_games_dir()
    gdir.mkdir(parents=True, exist_ok=True)
    checks.append({"name": "generated_games", "passed": True, "message": f"Generated games directory: {gdir}"})

    # Auto-fix
    prereqs_ok = all(c["passed"] for c in checks[:4])  # python, pip, pygame, pyyaml

    if auto_fix and prereqs_ok:
        # Fix missing packages
        if not checks[4]["passed"]:  # mcp
            fix_result = run(["pip3", "install", "mcp"], timeout=120)
            if fix_result.returncode == 0:
                fixes.append("Installed mcp package")

        if not checks[5]["passed"]:  # pygame_sdk
            # SDK should be local; nothing to pip install
            pass

    ready = all(c["passed"] for c in checks)
    return {"ready": ready, "checks": checks, "fixes_applied": fixes}
