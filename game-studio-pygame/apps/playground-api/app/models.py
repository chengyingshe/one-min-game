from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Request models ---


class GameCreate(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9][a-z0-9_-]*$", min_length=2, max_length=64)
    display_name: str = Field(..., min_length=1, max_length=128)
    description: str = Field("", max_length=2000)
    genre: str = Field("arcade", max_length=32)
    author_name: str = Field("", max_length=64)
    config_yaml: str = Field("", max_length=10000)
    screen_width: int = Field(800, ge=100, le=1920)
    screen_height: int = Field(600, ge=100, le=1080)
    controls: str = Field("", max_length=500)


class RunRequest(BaseModel):
    game_name: str
    duration_seconds: int = Field(10, ge=1, le=120)
    capture_frames: list[int] = Field(default_factory=lambda: [30, 60, 90, 120])


class RunResponse(BaseModel):
    screenshots: list[str]
    gif_url: Optional[str] = None
    exit_code: int
    duration_ms: int


class RatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    session_id: str = Field(..., min_length=1, max_length=128)


# --- Response models ---


class GameResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    genre: str
    author_name: str
    preview_image_url: Optional[str] = None
    screen_width: int
    screen_height: int
    controls: str
    is_template: bool = False
    play_count: int = 0
    avg_rating: float = 0.0
    rating_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
