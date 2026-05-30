"""Build (syntax-check + install deps) a Python game project."""

from __future__ import annotations

from pygame_studio_mcp.lib.exec_utils import run
from pygame_studio_mcp.lib.error_parser import parse_python_errors
from pygame_studio_mcp.lib.paths import project_dir


async def build_game(project: str) -> dict:
    """Syntax-check all .py files and install requirements."""
    dir_path = project_dir(project)

    if not dir_path.exists():
        return {
            "success": False,
            "errors": f"Project directory not found: {dir_path}",
        }

    all_errors: list[str] = []
    all_parsed: list[dict] = []

    # 1. Syntax-check all .py files with py_compile
    for py_file in sorted(dir_path.glob("*.py")):
        result = run(
            ["python3", "-m", "py_compile", str(py_file)],
            cwd=str(dir_path),
            timeout=30,
        )
        if result.returncode != 0:
            all_errors.append(result.stderr)
            parsed = parse_python_errors(result.stderr)
            for p in parsed:
                all_parsed.append({
                    "file": p.file,
                    "line": p.line,
                    "message": p.message,
                    "severity": p.severity,
                })

    # 2. Install requirements if requirements.txt exists
    req_file = dir_path / "requirements.txt"
    if req_file.exists():
        pip_result = run(
            ["pip3", "install", "-r", str(req_file)],
            cwd=str(dir_path),
            timeout=120,
        )
        if pip_result.returncode != 0:
            all_errors.append(f"pip install failed: {pip_result.stderr}")

    combined_errors = "\n".join(all_errors)
    success = len(all_errors) == 0

    result_dict: dict = {
        "success": success,
        "errors": combined_errors,
    }
    if all_parsed:
        result_dict["parsed_errors"] = all_parsed

    return result_dict
