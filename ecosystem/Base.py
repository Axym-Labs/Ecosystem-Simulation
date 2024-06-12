from dataclasses import dataclass
from typing import Callable
import numpy as np

@dataclass()
class Point():
    x: int
    y: int

    def AsTuple(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def AsTupleOfFloats(self) -> tuple[float, float]:
        return (float(self.x), float(self.y))
    

def clampToInt(value, min_value, max_value):
    return int(max(min_value, min(value, max_value)))

def safeCond(parameter, condition: Callable) -> bool:
    try:
        return condition(parameter)
    except IndexError:
        return False
    
def randomPoint(mapDimensions: tuple[int, int]) -> Point:
    return Point(
        x=clampToInt(np.random.randint(0, mapDimensions[0]), 0, mapDimensions[0]-1),
        y=clampToInt(np.random.randint(0, mapDimensions[1]), 0, mapDimensions[1]-1)
    )


def randomPointWithBias(mapDimensions: tuple[int, int], focusPoint: Point, bias: float) -> Point:
    return Point(
        x=clampToInt(np.random.normal(focusPoint.x, bias), 0, mapDimensions[0]-1),
        y=clampToInt(np.random.normal(focusPoint.y, bias), 0, mapDimensions[1]-1)
    )
def randomPointWithCenterBias(mapDimensions: tuple[int, int], bias: float) -> Point:
    center = Point(x=mapDimensions[0]//2, y=mapDimensions[1]//2)
    return randomPointWithBias(mapDimensions, center, bias)

class FocusPoint():
    focusPoints: list[Point]
    i: int = 0
    def __init__(self, mapDimensions: tuple[int, int], bias: float, numFocusPoints: int):
        self.focusPoints = [randomPoint(mapDimensions) for _ in range(numFocusPoints)]

    def getOne(self) -> Point:
        self.i += 1
        return self.focusPoints[(self.i-1) % len(self.focusPoints)]
    
