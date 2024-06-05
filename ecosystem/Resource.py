import numpy as np
from dataclasses import dataclass
from typing import Callable
from ecosystem.Base import *

@dataclass
class Resource():
    hash: int
    position: Point
    containedResources: np.ndarray

def createOneResource(hash: int, position: Point, resourceDistribution: np.ndarray) -> Resource:
    return Resource(
        hash=hash,
        position=position,
        containedResources=resourceDistribution
    )

def createResourcesRandomly(n: int, mapDims: tuple[int, int], resourceFn: Callable) -> list[Resource]:
    return [
        resourceFn()
        for _ in range(n)
    ]