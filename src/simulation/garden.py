import math
import os
from typing import Final, Tuple, Union

import numpy as np
import pyxel as px
from loguru import logger
from numpy import typing as npt

from src.funcs import clamp, linear_remap, decide
from src.helper.vec import Vec2
from src.simulation.cell import Bulb, Stem, Seed, Cell
from src.simulation.genome import Genome


class Plant:
    __MAX_AGE: Final = int(os.getenv("PLANT_MAX_AGE"))
    __ENERGY_PER_CELL: Final = int(os.getenv("PLANT_ENERGY_PER_CELL"))

    logger.info(f"Plant: max_age: {__MAX_AGE}")
    logger.info(f"Plant: energy_per_cell: {__ENERGY_PER_CELL}")

    def __init__(self, energy: int):
        self.__age = 0
        self.__energy = energy
        self.__energy_capacity = energy
        self.__alive = True

        logger.info(f"Plant@{id(self)} created. energy: {energy}")

    @property
    def alive(self):
        return self.__alive

    @property
    def energy(self):
        return self.__energy

    def check_alive(self):
        if self.__energy == 0 or self.__age > self.__MAX_AGE and self.alive:
            self.__alive = False
            logger.info(
                f"Plant@{id(self)} is dead. age: "
                f"{self.__age}, energy: {self.__energy}, capacity: {self.__energy_capacity}")

    def add_energy(self, amount: int):
        if not self.alive:
            return

        if amount < 0:
            logger.error(f"Adding negative amount of energy: {amount}")

        amount = min(amount, self.__energy_capacity - self.__energy)
        self.__energy += amount

    def take_energy(self, amount: int):
        if not self.alive:
            return 0

        amount = min(amount, self.__energy)
        self.__energy -= amount

        self.check_alive()
        return amount

    def increase_capacity(self):
        if not self.alive:
            return

        self.__energy_capacity += self.__ENERGY_PER_CELL

    def update_age(self):
        if not self.alive:
            return

        self.check_alive()
        self.__age += 1


class Garden:
    __SUN_LEVEL: Final = int(os.getenv("GARDEN_SUN_LEVEL"))
    __DENSITY_FACTOR: Final = int(os.getenv("GARDEN_DENSITY_FACTOR"))

    __MUTATION_RATE: Final = int(os.getenv("GARDEN_MUTATION_RATE"))
    __MUTATION_CHANCE: Final = float(os.getenv("GARDEN_MUTATION_CHANCE"))

    __INITIAL_ENERGY: Final = int(os.getenv("GARDEN_INITIAL_ENERGY"))

    __GENOME_SIZE: Final = 16
    __CHROMOSOME_LENGTH: Final = 4

    __HAS_PLANT: Final = (Bulb, Stem)
    __UPDATABLE: Final = (Bulb, Seed)
    __AFFECTS_ENERGY: Final = (Bulb, Stem, Seed)

    __ENERGY_COLORS: Final = (px.COLOR_NAVY, px.COLOR_PURPLE, px.COLOR_YELLOW)
    __SHADOW_COLORS: Final = (px.COLOR_GRAY, px.COLOR_NAVY)
    __ID_COLORS: Final = tuple(range(1, 15))

    TILE_SIZE: Final = 4

    logger.info(f"Garden: sun_level: {__SUN_LEVEL}")
    logger.info(f"Garden: density_factor: {__DENSITY_FACTOR}")
    logger.info(f"Garden: genome_size: {__GENOME_SIZE}")
    logger.info(f"Garden: chromosome_length: {__CHROMOSOME_LENGTH}")
    logger.info(f"Garden: mutation_rate: {__MUTATION_RATE}")
    logger.info(f"Garden: mutation_chance: {__MUTATION_CHANCE}")
    logger.info(f"Garden: initial_energy: {__INITIAL_ENERGY}")
    logger.info(f"Garden: tile_size: {TILE_SIZE}")

    def __init__(self, size: Tuple[int, int], border_color: int):
        self.__border_color = border_color
        self.__grid: npt.NDArray[Union[Cell, None]] = np.empty(size, Cell)
        self.__plants = set()

        mid_y, mid_x = map(lambda i: i // 2, self.__grid.shape)
        initial_seed = Seed(Genome.random(self.__GENOME_SIZE, self.__CHROMOSOME_LENGTH), self.__INITIAL_ENERGY, self)

        self.__grid[mid_y, mid_x] = initial_seed

        logger.info(f"Garden@{id(self)} created. size: {self.__grid.shape}")

    @property
    def size(self):
        return self.__grid.T.shape

    @property
    def has_plants(self):
        return len(self.__plants) != 0

    def __tile_x(self, x):
        return x % self.__grid.shape[1]

    def add_plant(self, plant: Plant):
        self.__plants.add(plant)

    def is_within(self, x: int, y: int):
        x = self.__tile_x(x)
        return 0 <= y < self.__grid.shape[0] and 0 <= x < self.__grid.shape[1]

    def is_available(self, x: int, y: int):
        x = self.__tile_x(x)
        return self.is_within(x, y) and self.__grid[y, x] is None

    def place_cell(self, cell: Cell, x: int, y: int):
        x = self.__tile_x(x)
        if self.__grid[y, x] is not None:
            logger.error(f"Grid at ({y}, {x}) is not empty")

        self.__grid[y, x] = cell

    def remove_cell(self, x: int, y: int):
        x = self.__tile_x(x)
        if self.__grid[y, x] is None:
            logger.warning(f"Grid at ({y}, {x}) is already empty")

        self.__grid[y, x] = None

    def get_cell(self, x: int, y: int):
        x = self.__tile_x(x)
        return self.__grid[y, x] if self.is_within(x, y) else None

    def replace_cell(self, cell: Cell, x: int, y: int):
        self.remove_cell(x, y)
        self.place_cell(cell, x, y)

    def draw_energy(self, position: Vec2):
        for x, col in enumerate(self.__grid.T):
            density_factor = self.__DENSITY_FACTOR
            sun_level = self.__SUN_LEVEL
            for y, row in enumerate(col):
                if not type(row) in self.__AFFECTS_ENERGY:
                    continue

                multiplier = sun_level * (density_factor > 0)

                color = self.__ENERGY_COLORS[
                    math.floor(linear_remap(multiplier,
                                            0, self.__SUN_LEVEL,
                                            0, len(self.__ENERGY_COLORS) - 1))
                ]

                px.rect(*(position + Vec2(x, y) * 4).as_tuple, self.TILE_SIZE, self.TILE_SIZE, color)

                density_factor -= 1
                sun_level = clamp(sun_level - 1, 0, self.__SUN_LEVEL)

    def draw_shadow(self, position: Vec2):
        for x, col in enumerate(self.__grid.T):
            is_shadow = False
            for y, row in enumerate(col):
                if row is not None:
                    is_shadow = True

                color = self.__SHADOW_COLORS[is_shadow]
                px.rect(*(position + Vec2(x, y) * 4).as_tuple, self.TILE_SIZE, self.TILE_SIZE, color)

    def draw_plants(self, position: Vec2):
        for (y, x), val in np.ndenumerate(self.__grid):
            if val is None:
                continue
            else:
                val: Cell
                val.image.draw(*(position + Vec2(x, y) * 4).as_tuple)

    def draw_plants_id(self, position: Vec2):
        for (y, x), val in np.ndenumerate(self.__grid):
            if not type(val) in self.__HAS_PLANT:
                continue
            else:
                color = self.__ID_COLORS[id(val.plant) % len(self.__ID_COLORS)]
                px.rect(*(position + Vec2(x, y) * 4).as_tuple, self.TILE_SIZE, self.TILE_SIZE, color)

    def draw_border(self, position: Vec2):
        shape_vec = Vec2(*self.__grid.T.shape)
        px.rectb(*(position - Vec2(1, 1)).as_tuple, *(shape_vec * 4 + Vec2(2, 2)).as_tuple, self.__border_color)

    def update(self):
        self.update_energy()
        self.update_cells()
        self.update_plants_age()
        self.update_dead_plants()

    def update_energy(self):
        for x, col in enumerate(self.__grid.T):
            density_factor = self.__DENSITY_FACTOR
            sun_level = self.__SUN_LEVEL
            for y, row in enumerate(col):
                if not type(row) in self.__AFFECTS_ENERGY:
                    continue

                row: Cell

                multiplier = sun_level * (density_factor > 0)

                row.produce_energy(multiplier)
                row.consume_energy()

                density_factor -= 1
                sun_level = clamp(sun_level - 1, 0, self.__SUN_LEVEL)

    def update_dead_plants(self):
        for (y, x), val in np.ndenumerate(self.__grid):
            if not type(val) in self.__HAS_PLANT:
                continue

            val: Cell

            if val.plant.alive:
                continue

            self.__plants.discard(val.plant)

            if type(val) is not Bulb:
                self.remove_cell(x, y)
                continue

            val: Bulb

            if val.energy == 0:
                self.remove_cell(x, y)
                continue

            genome = val.copy_of_genome
            if decide(self.__MUTATION_CHANCE):
                [genome.mutate((0, self.__GENOME_SIZE - 1)) for _ in range(self.__MUTATION_RATE)]
            seed = Seed(genome, self.__INITIAL_ENERGY, self)
            self.replace_cell(seed, x, y)

    def update_plants_age(self):
        for plant in self.__plants:
            plant.update_age()

    def update_cells(self):
        for (y, x), val in np.ndenumerate(self.__grid.copy()):
            if not type(val) in self.__UPDATABLE:
                continue

            val: Cell
            val.update(x, y)
