import numpy as np
import time
import pygame
from typing import Callable
from dataclasses import dataclass
from ecosystem.Creature import Creature
from ecosystem.Resource import Resource

@dataclass(frozen=True)
class GameConfiguration:
    FPS: int
    OtherOptions: dict

    MapDimensions: tuple[int, int]
    CreatureLimit: int

    ResourceDensity: float
    MaxResourceValue: float
    ResourceLength: int

    TileSize: int
    MaxInteractionDistance: int
    MaxConsumptionDistance: int
    CreatureStepSize: int
    
    ConstructiveInteractionDivisor: float
    WinnerGetsAllDivisor: float
    ProductionDivisor: float
    ReproductiveInteractionDivisor: float
    BiparentalReproductiveInteractionDivisor: float

    ResourceDepletionRate: float
    HealthDepletionRate: float
    HealthGainRate: float
    MaxHealth: float

@dataclass
class GameLogic:
    HashFn: Callable
    ContainedResourceFn: Callable

    DeathCondition: Callable
    TooFewResourcesFn: Callable

    ForceExitCondition: Callable

    BornCreatureFn: Callable
    BiparentalBornCreatureFn: Callable

    CreateResourceFn: Callable

@dataclass
class GameState():
    Running: bool

    Creatures: list[Creature]
    Resources: list[Resource]


@dataclass
class GameRunningConfig():
    Debug: bool
    PrintStats: bool
    SaveActions: bool
    SavePerformanceInfo: bool
    OnEnd: Callable = lambda game: None

@dataclass
class Game():
    Conf: GameConfiguration
    Logic: GameLogic
    State: GameState
    RunningConfig: GameRunningConfig
