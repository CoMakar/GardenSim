from typing import Protocol

from src.helper.vec import Vec2


class Positionable(Protocol):
    @property
    def position(self) -> Vec2:
        pass
