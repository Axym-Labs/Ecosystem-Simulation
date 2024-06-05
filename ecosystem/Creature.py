from typing import NamedTuple
import numpy as np
from dataclasses import dataclass
from dataclasses import field
from ecosystem.Genome import GenomeScalar
from typing import Callable
from ecosystem.Base import *

@dataclass(frozen=True)
class CreatureBasis():
    genome: GenomeScalar
    
@dataclass()
class CreatureSituation():
    age: int
    health: float
    resources: np.ndarray
    position: Point

    # deadFor = -1

@dataclass()
class Creature():
    hash: int
    base: CreatureBasis
    situation: CreatureSituation
    actionDescriptions: list[str]
    
def createOneCreature(hash: int, genome: GenomeScalar, resources: np.ndarray, positionFn: Callable) -> Creature:
    return Creature(
        hash,
        CreatureBasis(
            genome=genome
        ),
        CreatureSituation(
            age=0,
            health=1,
            resources=resources,
            position=positionFn()
        ),
        []
    )

def createCreaturesRandomly(n: int, mapDims: tuple[int, int], creatureFn: Callable) -> list[Creature]:
    return [
        creatureFn()
        for _ in range(n)
    ]