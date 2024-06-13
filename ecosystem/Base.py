from dataclasses import dataclass
from typing import Callable
from enum import Enum
from typing import List, Tuple
import numpy as np

@dataclass()
class Point():
    x: int
    y: int

    def AsTuple(self) -> tuple[int, int]:
        return (self.x, self.y)
    
    def AsTupleOfFloats(self) -> tuple[float, float]:
        return (float(self.x), float(self.y))
    
    def WithinRanges(self, x_start, x_end, y_start, y_end) -> bool:
        "inclusive"
        return self.x >= x_start and self.x <= x_end and self.y >= y_start and self.y <= y_end
    
class DecisionFnType(Enum):
    GetOneAction = 1
    GetAllActionsSorted = 2
    

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

def MapBoundariesAroundPosition(mapDimensions: tuple[int, int], position: Point, blockDistance: int) -> Tuple[int,int,int,int]:
    x_start = clampToInt(position.x - blockDistance, 0, mapDimensions[0])
    x_end = clampToInt(position.x + blockDistance, 0, mapDimensions[0])
    y_start = clampToInt(position.y - blockDistance, 0, mapDimensions[1])
    y_end = clampToInt(position.y + blockDistance, 0, mapDimensions[1])

    return x_start, x_end, y_start, y_end

class FocusPoint():
    focusPoints: list[Point]
    i: int = 0
    def __init__(self, mapDimensions: tuple[int, int], numFocusPoints: int):
        self.focusPoints = [randomPoint(mapDimensions) for _ in range(numFocusPoints)]

    def getOne(self) -> Point:
        self.i += 1
        return self.focusPoints[(self.i-1) % len(self.focusPoints)]
    
