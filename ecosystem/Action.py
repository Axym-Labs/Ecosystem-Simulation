from enum import Enum
import numpy as np
from enum import Enum
from ecosystem.Game import Game
from ecosystem.Base import *

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


def IsActionValid(game: Game, creatureIndex: int, action: Action) -> bool:

    if action == Action.Stay or action == Action.Die or action == Action.Produce:
        return True

    elif action == Action.Reproduce:
        return len(game.State.Creatures) < game.Configuration.CreatureLimit

    elif action == Action.Consume:
        resourceIndex = findClosestResourceIndex(game, creatureIndex)
        return closeTo(game.State.Creatures[creatureIndex].situation.position, game.State.Resources[resourceIndex].position, game.Configuration.MaxConsumptionDistance)

    elif action in [Action.MoveLeft, Action.MoveRight, Action.MoveUp, Action.MoveDown]:
        creature = game.State.Creatures[creatureIndex]
        step = game.Configuration.CreatureStepSize

        if action == Action.MoveLeft:
            stepLeftPos = Point(creature.situation.position.x - step, creature.situation.position.y)
            return game.State.Creatures[creatureIndex].situation.position.x > 0 and noOverlap(game, stepLeftPos)
        
        if action == Action.MoveRight:
            stepRightPos = Point(creature.situation.position.x + step, creature.situation.position.y)
            return game.State.Creatures[creatureIndex].situation.position.x < game.Configuration.MapDimensions[0] -1 and noOverlap(game, stepRightPos)

        if action == Action.MoveUp:
            stepUpPos = Point(creature.situation.position.x, creature.situation.position.y - step)
            return game.State.Creatures[creatureIndex].situation.position.y > 0 and noOverlap(game, stepUpPos)

        if action == Action.MoveDown:
            stepDownPos = Point(creature.situation.position.x, creature.situation.position.y + step)
            return game.State.Creatures[creatureIndex].situation.position.y < game.Configuration.MapDimensions[1] -1 and noOverlap(game, stepDownPos)

    elif action in [Action.NeutralExchange, Action.ConstructiveExchange, Action.DestructiveExchange, Action.LethalExchange, Action.ReproduceBiparentally]:
        otherCreatureIndex = findClosestCreatureIndex(game, creatureIndex)

        if action == Action.ReproduceBiparentally and not len(game.State.Creatures) < game.Configuration.CreatureLimit:
            return False
        
        return closeTo(game.State.Creatures[creatureIndex].situation.position, game.State.Creatures[otherCreatureIndex].situation.position, game.Configuration.MaxInteractionDistance)

    raise NotImplementedError(f"Action {action} not implemented.")

def closeTo(pos1: Point, pos2: Point, maxDistance: int) -> bool:
    return bool(np.linalg.norm(np.array(pos1.AsTuple()) - np.array(pos2.AsTuple())) < maxDistance)

def findClosestCreatureIndex(game: Game, creatureIndex: int) -> int:
    creature = game.State.Creatures[creatureIndex]
    other_creatures = [
        c
        for i, c in enumerate(game.State.Creatures)
        if i != creatureIndex
    ]

    return int(np.argmin([
        np.linalg.norm(np.array(creature.situation.position.AsTuple()) - np.array(other_creature.situation.position.AsTuple()))
        for other_creature in other_creatures
    ]))

def findClosestResourceIndex(game: Game, creatureIndex: int) -> int:
    creature = game.State.Creatures[creatureIndex]
    resources = game.State.Resources

    return int(np.argmin([
        np.linalg.norm(np.array(creature.situation.position.AsTuple()) - np.array(resource.position.AsTuple()))
        for resource in resources
    ]))
    
def noOverlap(game: Game, point: Point) -> bool:
    return not any([
        c.situation.position.x == point.x and c.situation.position.y == point.y
        for c in game.State.Creatures
    ])