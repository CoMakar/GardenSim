from typing import Union

import pyxel as px

from src.helper.vec import Vec2
from src.types import Number


class Image:
    def __init__(self, width: Number, height: Number,
                 u: Number, v: Number,
                 bank: Union[int, px.Image], transparency_key: Union[int, None] = None):
        self.__size = Vec2(width, height)
        self.__uv = Vec2(u, v)

        self.__bank = bank
        self.__transparency_key = transparency_key

    def draw(self, x: Number, y: Number):
        px.blt(x, y, self.__bank,
               *self.__uv.as_tuple, *self.__size.as_tuple,
               self.__transparency_key)
