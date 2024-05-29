import os
import random as rnd
from typing import Final, Tuple, List

from loguru import logger

from src.funcs import decide


class Gene:
    ACTIVE_CHANCE: Final = float(os.getenv("GENE_ACTIVE_CHANCE"))

    logger.info(f"Gene: active_chance: {ACTIVE_CHANCE}")

    def __init__(self, dna: int, active: bool):
        self.__dna = dna
        self.__active = active

    @property
    def dna(self):
        return self.__dna

    @property
    def active(self):
        return self.__active

    def mutate(self, deviation_range: Tuple[int, int]):
        self.__dna = rnd.randint(deviation_range[0], deviation_range[1])
        self.__active = decide(self.ACTIVE_CHANCE)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.dna}, {self.active})"

    def copy(self):
        return Gene(self.dna, self.active)


class Chromosome:
    def __init__(self, genes: List[Gene]):
        self.__genes = genes

    @property
    def genes(self):
        return self.__genes.copy()

    @property
    def size(self):
        return len(self.__genes)

    def mutate(self, deviation_range: Tuple[int, int]):
        gene = rnd.choice(self.__genes)
        gene.mutate(deviation_range)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.__genes})"

    def copy(self):
        return Chromosome([d.copy() for d in self.__genes])


class Genome:
    def __init__(self, chromosomes: List[Chromosome]):
        self.__chromosomes = chromosomes
        self.__active_chromosome = 0

    @property
    def size(self):
        return len(self.__chromosomes)

    @property
    def chromosomes(self):
        return self.__chromosomes.copy()

    @property
    def chromosome(self):
        return self.__chromosomes[self.__active_chromosome]

    def set_active_gene(self, index: int):
        if index > len(self.__chromosomes):
            raise ValueError("Index out of range")

        self.__active_chromosome = index

    def mutate(self, deviation_range: Tuple[int, int]):
        logger.info(f"Genome@{id(self)} mutated")
        chromosome = rnd.choice(self.__chromosomes)
        chromosome.mutate(deviation_range)

    @staticmethod
    def random(size: int, chromosome_length: int):
        return Genome(
            [
                Chromosome(
                    [
                        Gene(rnd.randint(0, size - 1), decide(Gene.ACTIVE_CHANCE), ) for _ in range(chromosome_length)
                    ]
                ) for _ in range(size)]
        )

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.__chromosomes})"

    def copy(self):
        genome = Genome([c.copy() for c in self.__chromosomes])
        return genome
