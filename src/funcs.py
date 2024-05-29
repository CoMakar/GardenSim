import random as rnd

from src.types import Number


def clamp(number: Number, min_val: Number, max_val: Number):
    if max_val < min_val:
        raise ValueError("Required: max_val >= min_val")

    return max(min(number, max_val), min_val)


def decide(probability: float):
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Required: 0.0 <= probability <= 1.0:")

    return rnd.random() < probability


def linear_remap(value: Number,
                 from_min: Number, from_max: Number,
                 to_min: Number, to_max: Number):
    if from_min >= from_max:
        raise ValueError("Required: from_min < from_max")
    if to_min >= to_max:
        raise ValueError("Required: to_min < to_max")

    scale = (value - from_min) / (from_max - from_min)
    return to_min + scale * (to_max - to_min)
