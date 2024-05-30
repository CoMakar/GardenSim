from typing import List, Union

import pyxel as px

from src.helper.vec import Vec2
from src.protocols import Positionable


class Label:
    def __init__(self, position: Vec2, lines: List[str], color: int, relative_to: Union[Positionable, None] = None):
        self.__position = position
        self.__lines = lines
        self.__color = color
        self.__relative_to = relative_to
        self.__visible = True

    @property
    def position(self):
        if self.__relative_to is None:
            return self.__position
        else:
            return self.__relative_to.position + self.__position

    def add_line(self, line: str):
        self.__lines.append(line)

    def set_text(self, text: str):
        self.__lines = [text]

    def clear(self):
        self.__lines = []

    def draw(self):
        if not self.__visible:
            return

        if self.__relative_to is None:
            x, y = self.__position.as_tuple
        else:
            x, y = (self.__relative_to.position + self.__position).as_tuple

        for line in self.__lines:
            px.text(x, y, line, self.__color)
            y += 10
