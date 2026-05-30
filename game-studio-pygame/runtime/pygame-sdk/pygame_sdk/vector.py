"""2D vector math for game physics and positioning."""
from __future__ import annotations

import math


class Vector2D:
    """Immutable-style 2D vector with full math operations.

    Uses __slots__ for performance in hot loops.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    def add(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def sub(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def scale(self, s: float) -> Vector2D:
        return Vector2D(self.x * s, self.y * s)

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> Vector2D:
        l = self.length()
        if l == 0:
            return Vector2D()
        return Vector2D(self.x / l, self.y / l)

    def distance_to(self, other: Vector2D) -> float:
        return self.sub(other).length()

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2D) -> float:
        return self.x * other.y - self.y * other.x

    def rotate(self, angle: float) -> Vector2D:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )

    def lerp(self, other: Vector2D, t: float) -> Vector2D:
        return Vector2D(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def reflect(self, normal: Vector2D) -> Vector2D:
        d = self.dot(normal) * 2
        return Vector2D(self.x - normal.x * d, self.y - normal.y * d)

    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    def perpendicular(self) -> Vector2D:
        return Vector2D(-self.y, self.x)

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))
