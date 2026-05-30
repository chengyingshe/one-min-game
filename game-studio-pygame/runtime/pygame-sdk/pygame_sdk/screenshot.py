"""Screenshot capture for playground integration."""
from __future__ import annotations

import io

import pygame


def capture_screenshot(surface: pygame.Surface) -> bytes:
    """Capture a pygame surface as PNG bytes.

    Returns empty bytes on failure.
    """
    try:
        buf = io.BytesIO()
        pygame.image.save(surface, buf, "PNG")
        return buf.getvalue()
    except Exception:
        return b""
