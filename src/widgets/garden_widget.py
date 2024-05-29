from typing import Union, Literal

import pyxel as px

from src.helper.vec import Vec2
from src.simulation.garden import Garden


class GardenWidget:
    def __init__(self, garden: Garden, position: Vec2):
        self.__garden = garden
        self.__position = position

    @property
    def position(self):
        return self.__position

    @property
    def size(self):
        return tuple(map(lambda s: s * Garden.TILE_SIZE, self.garden.size))

    @property
    def garden(self):
        return self.__garden

    @garden.setter
    def garden(self, value):
        self.__garden = value

    def draw(self, draw_mode: Union[Literal["draw_plants", "draw_plants_id", "draw_shadow", "draw_energy"], str]):
        px.rect(*self.position.as_tuple, *self.size, px.COLOR_BLACK)
        getattr(self.__garden, draw_mode)(self.position)
        self.garden.draw_border(self.position)

    def update(self):
        self.garden.update()
