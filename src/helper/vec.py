import math
from dataclasses import dataclass
from typing import Any

from src.types import Number


@dataclass(frozen=True)
class Vec2:
    x: Number
    y: Number

    @property
    def as_tuple(self):
        return (self.x, self.y)

    @staticmethod
    def __is_vector(other: Any):
        if not isinstance(other, Vec2):
            raise TypeError(f"Required: type(other) = Vec2; Got {type(other) = }")

    @staticmethod
    def __is_scalar(other: Any):
        if not isinstance(other, Number):
            raise TypeError(f"Required: type(scalar) = float | int; Got: {type(other) = }")

    def __add__(self, other: 'Vec2'):
        self.__is_vector(other)
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2'):
        self.__is_vector(other)
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Number):
        self.__is_scalar(scalar)
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: Number):
        self.__is_scalar(scalar)
        return Vec2(self.x / scalar, self.y / scalar)

    def __rmul__(self, scalar: Number):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __eq__(self, other: Any):
        if not isinstance(other, Vec2):
            return False

        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"{{{self.x}, {self.y}}}"

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def normalized(self):
        return Vec2(0, 0) if self.length == 0 else Vec2(self.x / self.length, self.y / self.length)
