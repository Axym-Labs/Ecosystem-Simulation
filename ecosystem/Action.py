from enum import Enum
from enum import Enum
from ecosystem.Base import *
import numpy as np

class Action(Enum):
    Stay = 1
    Consume = 2
    Produce = 3
    Die = 4
    Reproduce = 5

    # Directed Actions
    MoveUp = 6
    MoveDown = 7	
    MoveLeft = 8
    MoveRight = 9

    # Interactions
    NeutralExchange = 10
    ConstructiveExchange = 11
    DestructiveExchange = 12
    LethalExchange = 13
    ReproduceBiparentally = 14

    MoveSomeWhere = 15