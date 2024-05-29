import os
import random as rnd
from abc import ABC, abstractmethod
from typing import Final, TYPE_CHECKING

from loguru import logger

from src.helper.vec import Vec2
from src.simulation import garden as gd
from src.simulation.genome import Genome
from src.widgets.image import Image

if TYPE_CHECKING:
    from src.simulation.garden import Garden, Plant


class Cell(ABC):
    def __init__(self, garden: 'Garden' = None, plant: 'Plant' = None):
        self._image = Image(4, 4, 0, 0, 0)
        self._energy_consumption = 0
        self._energy_gain = 0
        self._garden = garden
        self._plant = plant

    @property
    def garden(self):
        if self._garden is None:
            logger.error(f"{self.__class__.__qualname__} does not belong to garden")

        return self._garden

    @property
    def plant(self):
        if self._plant is None:
            logger.error(f"{self.__class__.__qualname__} does not belong to plant")

        return self._plant

    @property
    def image(self):
        return self._image

    @garden.setter
    def garden(self, value: 'Garden'):
        self._garden = value

    @plant.setter
    def plant(self, value: 'Plant'):
        self._plant = value

    @abstractmethod
    def produce_energy(self, multiplier: int):
        pass

    @abstractmethod
    def consume_energy(self):
        pass

    @abstractmethod
    def update(self, x: int, y: int):
        pass


class Stem(Cell):
    __IMAGES: Final = (
        Image(4, 4, 4, 0, 0),
        Image(4, 4, 8, 0, 0),
        Image(4, 4, 12, 0, 0),
        Image(4, 4, 0, 4, 0),
        Image(4, 4, 4, 4, 0),
        Image(4, 4, 8, 4, 0),
        Image(4, 4, 12, 4, 0),
    )

    def __init__(self, plant: 'Plant' = None):
        super().__init__(plant=plant)
        self._image = rnd.choice(self.__IMAGES)
        self._energy_consumption = 30
        self._energy_gain = 10

    def produce_energy(self, multiplier: int):
        self.plant.add_energy(self._energy_gain * multiplier)

    def consume_energy(self):
        self.plant.take_energy(self._energy_consumption)

    def update(self, x: int, y: int):
        pass


class Bulb(Cell):
    __POS_DELTAS: Final = (Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0))
    __IMAGES: Final = (
        Image(4, 4, 4, 8, 0),
        Image(4, 4, 8, 8, 0),
        Image(4, 4, 12, 8, 0)
    )

    __ENERGY_TO_GROW: Final = int(os.getenv("BULB_ENERGY_TO_GROW"))

    logger.info(f"Bulb: energy_to_grow: {__ENERGY_TO_GROW}")

    def __init__(self, genome: Genome, energy: int = 0, garden: 'Garden' = None, plant: 'Plant' = None):
        super().__init__(garden, plant)
        self._image = rnd.choice(self.__IMAGES)
        self._energy_consumption = 40
        self._energy_gain = 2

        self.__genome = genome
        self.__energy = energy

        for chromosome in self.__genome.chromosomes:
            if chromosome.size != len(self.__POS_DELTAS):
                logger.error(f"len(directions): {len(self.__POS_DELTAS)} != chromosome.size: {chromosome.size}")

    @property
    def copy_of_genome(self):
        return self.__genome.copy()

    @property
    def energy(self):
        return self.__energy

    def produce_energy(self, multiplier: int):
        self.__energy += self._energy_gain * multiplier

    def consume_energy(self):
        self.plant.take_energy(self._energy_consumption)

    def update(self, x: int, y: int):
        if self.__energy < self.__ENERGY_TO_GROW:
            return

        for delta, dna in zip(self.__POS_DELTAS, self.__genome.chromosome.genes):
            if not self.garden.is_available(x + delta.x, y + delta.y) or not dna.active:
                continue

            bulb = Bulb(self.copy_of_genome, 1, self.garden, self.plant)
            bulb.__genome.set_active_gene(dna.dna)

            self.garden.place_cell(bulb, x + delta.x, y + delta.y)

        stem = Stem(self.plant)
        self.plant.increase_capacity()
        self.garden.replace_cell(stem, x, y)


class Seed(Cell):
    __IMAGES: Final = Image(4, 4, 0, 8, 0)

    def __init__(self, genome: Genome, energy: int, garden: 'Garden' = None):
        super().__init__(garden)
        self._image = self.__IMAGES
        self.__genome = genome
        self.__energy = energy

    @property
    def energy(self):
        return self.__energy

    def produce_energy(self, multiplier: int):
        pass

    def consume_energy(self):
        pass

    def update(self, x: int, y: int):
        if self.garden.is_available(x, y + 1):
            self.garden.remove_cell(x, y)
            self.garden.place_cell(self, x, y + 1)
            return

        if not self.garden.is_within(x, y + 1) and self.energy != 0:
            bulb = Bulb(self.__genome, 0, self.garden, gd.Plant(self.energy))

            self.garden.replace_cell(bulb, x, y)
            self.garden.add_plant(bulb.plant)
            return

        self.garden.remove_cell(x, y)
