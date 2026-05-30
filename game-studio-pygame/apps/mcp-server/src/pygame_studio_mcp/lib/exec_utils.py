"""Process execution with timeout support."""

from __future__ import annotations

import subprocess
from typing import Mapping, Sequence

from pygame_studio_mcp.types import ExecResult


def run(
    command: Sequence[str],
    *,
    cwd: str | None = None,
    timeout: float | None = None,
    env: Mapping[str, str] | None = None,
) -> ExecResult:
    """Run a subprocess and return structured result."""
    import os

    full_env = {**os.environ}
    if env:
        full_env.update(env)

    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            env=full_env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return ExecResult(
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        return ExecResult(
            stdout="",
            stderr=f"Process timed out after {timeout}s",
            returncode=None,
            timed_out=True,
        )
    except FileNotFoundError:
        return ExecResult(
            stdout="",
            stderr=f"Command not found: {command[0]}",
            returncode=None,
            timed_out=False,
        )
    except Exception as exc:
        return ExecResult(
            stdout="",
            stderr=str(exc),
            returncode=None,
            timed_out=False,
        )
