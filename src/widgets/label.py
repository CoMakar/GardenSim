from typing import List

import pyxel as px

from src.helper.vec import Vec2


class Label:
    def __init__(self, position: Vec2, lines: List[str], color: int, relative_to=None):
        self.__position = position
        self.__lines = lines
        self.__color = color
        self.__relative_to = relative_to
        self.__visible = True

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
