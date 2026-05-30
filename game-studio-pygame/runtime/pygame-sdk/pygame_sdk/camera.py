"""Camera system with follow, offset, first-person, and fixed modes."""
from __future__ import annotations

from enum import IntEnum

from .collision import Rect
from .entity import Entity
from .vector import Vector2D


class CameraMode(IntEnum):
    FOLLOW = 0
    OFFSET = 1
    FIRST_PERSON = 2
    FIXED = 3


class Camera:
    """Camera with multiple tracking modes and coordinate transforms."""

    def __init__(
        self,
        position: Vector2D | None = None,
        mode: CameraMode = CameraMode.FOLLOW,
        target: Entity | None = None,
        offset: Vector2D | None = None,
        bounds: Rect | None = None,
        direction: float = 0.0,
        fov_angle: float = 1.047,
        lerp_factor: float = 0.15,
    ) -> None:
        self.position = position if position is not None else Vector2D()
        self.mode = mode
        self.target = target
        self.offset = offset if offset is not None else Vector2D()
        self.bounds = bounds if bounds is not None else Rect()
        self.direction = direction
        self.fov_angle = fov_angle
        self.lerp_factor = lerp_factor

    @classmethod
    def follow_camera(cls, target: Entity) -> Camera:
        return cls(mode=CameraMode.FOLLOW, target=target, lerp_factor=0.15)

    @classmethod
    def offset_camera(
        cls, target: Entity, offset_x: float, offset_y: float
    ) -> Camera:
        return cls(
            mode=CameraMode.OFFSET,
            target=target,
            offset=Vector2D(offset_x, offset_y),
            lerp_factor=0.1,
        )

    @classmethod
    def first_person_camera(
        cls, position: Vector2D, direction: float
    ) -> Camera:
        return cls(
            position=position,
            mode=CameraMode.FIRST_PERSON,
            direction=direction,
            fov_angle=1.047,
        )

    @classmethod
    def fixed_camera(cls, x: float, y: float) -> Camera:
        return cls(position=Vector2D(x, y), mode=CameraMode.FIXED)

    def update(self) -> None:
        """Update camera position based on mode."""
        if self.mode == CameraMode.FOLLOW:
            if self.target is not None:
                target_pos = self.target.pos
                if self.lerp_factor <= 0 or self.lerp_factor >= 1:
                    self.position = target_pos
                else:
                    self.position = self.position.lerp(target_pos, self.lerp_factor)

        elif self.mode == CameraMode.OFFSET:
            if self.target is not None:
                target_pos = self.target.pos.add(self.offset)
                self.position = self.position.lerp(target_pos, self.lerp_factor)

        elif self.mode == CameraMode.FIRST_PERSON:
            if self.target is not None:
                self.position = self.target.pos

        self._clamp_to_bounds()

    def _clamp_to_bounds(self) -> None:
        """Keep camera within configured bounds."""
        if self.bounds.w > 0 and self.bounds.h > 0:
            self.position.x = max(self.bounds.x, min(self.position.x, self.bounds.x + self.bounds.w))
            self.position.y = max(self.bounds.y, min(self.position.y, self.bounds.y + self.bounds.h))

    def world_to_screen(
        self, world_pos: Vector2D, screen_w: int, screen_h: int
    ) -> tuple[int, int, bool]:
        """Convert world coordinates to screen coordinates.

        Returns (screen_x, screen_y, visible).
        """
        sx = int(world_pos.x - self.position.x + screen_w / 2)
        sy = int(world_pos.y - self.position.y + screen_h / 2)
        visible = 0 <= sx < screen_w and 0 <= sy < screen_h
        return sx, sy, visible

    def screen_to_world(
        self, screen_x: int, screen_y: int, screen_w: int, screen_h: int
    ) -> Vector2D:
        """Convert screen coordinates to world coordinates."""
        return Vector2D(
            float(screen_x) + self.position.x - screen_w / 2,
            float(screen_y) + self.position.y - screen_h / 2,
        )

    def forward(self) -> Vector2D:
        """Return the forward direction vector based on camera angle."""
        return Vector2D(1, 0).rotate(self.direction)

    def right(self) -> Vector2D:
        """Return the right direction vector (perpendicular to forward)."""
        return self.forward().perpendicular()

    def rotate_left(self, angle: float) -> None:
        self.direction -= angle

    def rotate_right(self, angle: float) -> None:
        self.direction += angle

    def move_forward(self, dist: float) -> None:
        self.position = self.position.add(self.forward().scale(dist))

    def move_right(self, dist: float) -> None:
        self.position = self.position.add(self.right().scale(dist))
