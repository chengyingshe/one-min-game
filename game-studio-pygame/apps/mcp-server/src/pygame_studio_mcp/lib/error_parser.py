"""Python traceback / error parsing."""

from __future__ import annotations

import re

from pygame_studio_mcp.types import ParsedError


def parse_python_errors(stderr: str) -> list[ParsedError]:
    """Parse Python tracebacks from stderr output.

    Handles patterns like:
      File "main.py", line 42, in <module>
        x = undefined_var
        ^
      NameError: name 'undefined_var' is not defined

    And also syntax errors:
      File "main.py", line 10
        def foo(:
               ^
      SyntaxError: invalid syntax
    """
    errors: list[ParsedError] = []

    # Pattern for "File X, line Y" lines
    file_line_re = re.compile(r'^\s*File "(.+?\.py)", line (\d+)', re.MULTILINE)
    # Pattern for the error type + message on a line by itself
    error_re = re.compile(r"^(\w+Error|\w+Warning|\w+Exception): (.+)$", re.MULTILINE)

    # Collect file/line pairs
    file_lines: list[tuple[str, int]] = []
    for m in file_line_re.finditer(stderr):
        file_lines.append((m.group(1), int(m.group(2))))

    # Collect error messages
    error_msgs: list[tuple[str, str]] = []
    for m in error_re.finditer(stderr):
        etype = m.group(1)
        emsg = m.group(2)
        severity = "warning" if "Warning" in etype else "error"
        error_msgs.append((severity, f"{etype}: {emsg}"))

    # Pair them up: last file/line with the error message
    if file_lines and error_msgs:
        fpath, line = file_lines[-1]
        severity, message = error_msgs[-1]
        errors.append(ParsedError(file=fpath, line=line, message=message, severity=severity))  # type: ignore[arg-type]
    elif error_msgs:
        severity, message = error_msgs[-1]
        errors.append(
            ParsedError(file="", line=0, message=message, severity=severity)  # type: ignore[arg-type]
        )

    # Also look for py_compile syntax check errors
    # py_compile outputs: File "path", line N
    # followed by the offending line and a caret
    if not errors:
        syntax_re = re.compile(
            r'^(.+?\.py):(\d+):\s*(.+)$', re.MULTILINE
        )
        for m in syntax_re.finditer(stderr):
            errors.append(
                ParsedError(
                    file=m.group(1),
                    line=int(m.group(2)),
                    message=m.group(3),
                    severity="error",
                )
            )

    return errors
