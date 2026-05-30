"""Difficulty tier definitions for game balancing."""
from __future__ import annotations

from dataclasses import dataclass


class DifficultyTier:
    """String constants for difficulty tiers."""

    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


@dataclass
class DifficultyParams:
    """Parameters controlling game difficulty for a single tier."""

    tier: str = "normal"
    gravity: float = 0.18
    speed: float = 1.0
    spawn_rate: int = 30
    grace_period: int = 25
    hp_bonus: int = 0
    gap_size: int = 0
    flap_impulse: float = 0.0
