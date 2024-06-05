from dataclasses import dataclass
from typing import Callable


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