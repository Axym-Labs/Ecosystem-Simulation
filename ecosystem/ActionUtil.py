from typing import Callable
import random
import numpy as np
from ecosystem.Game import Game
from ecosystem.Base import Point, DecisionFnType
from ecosystem import Resource
from ecosystem import ResourceUtil
from ecosystem import Action

def IsActionValid(game: Game, creatureIndex: int, action: Action.Action) -> bool:

    if 'BlockInteraction' in game.Conf.OtherOptions and action in [Action.Action.NeutralExchange, Action.Action.ConstructiveExchange, Action.Action.DestructiveExchange, Action.Action.LethalExchange, Action.Action.ReproduceBiparentally]:
        return False
    if 'BlockProduction' in game.Conf.OtherOptions and action == Action.Action.Produce:
        return False

    if action == Action.Action.Stay or action == Action.Action.Die or action == Action.Action.Produce:
        return True

    elif action == Action.Action.Reproduce:
        return len(game.State.Creatures) < game.Conf.CreatureLimit

    elif action == Action.Action.Consume:
        resourceIndex = findClosestResourceIndex(game, creatureIndex)
        return closeTo(game.State.Creatures[creatureIndex].situation.position, game.State.Resources[resourceIndex].position, game.Conf.MaxConsumptionDistance)

    elif action in [Action.Action.MoveLeft, Action.Action.MoveRight, Action.Action.MoveUp, Action.Action.MoveDown]:
        creature = game.State.Creatures[creatureIndex]
        step = game.Conf.CreatureStepSize

        if action == Action.Action.MoveLeft:
            stepLeftPos = Point(creature.situation.position.x - step, creature.situation.position.y)
            return game.State.Creatures[creatureIndex].situation.position.x > 0 and noOverlap(game, stepLeftPos)
        
        if action == Action.Action.MoveRight:
            stepRightPos = Point(creature.situation.position.x + step, creature.situation.position.y)
            return game.State.Creatures[creatureIndex].situation.position.x < game.Conf.MapDimensions[0] -1 and noOverlap(game, stepRightPos)

        if action == Action.Action.MoveUp:
            stepUpPos = Point(creature.situation.position.x, creature.situation.position.y - step)
            return game.State.Creatures[creatureIndex].situation.position.y > 0 and noOverlap(game, stepUpPos)

        if action == Action.Action.MoveDown:
            stepDownPos = Point(creature.situation.position.x, creature.situation.position.y + step)
            return game.State.Creatures[creatureIndex].situation.position.y < game.Conf.MapDimensions[1] -1 and noOverlap(game, stepDownPos)

    elif action in [Action.Action.NeutralExchange, Action.Action.ConstructiveExchange, Action.Action.DestructiveExchange, Action.Action.LethalExchange, Action.Action.ReproduceBiparentally]:
        otherCreatureIndex = findClosestCreatureIndex(game, creatureIndex)

        if action == Action.Action.ReproduceBiparentally and not len(game.State.Creatures) < game.Conf.CreatureLimit:
            return False
        
        return closeTo(game.State.Creatures[creatureIndex].situation.position, game.State.Creatures[otherCreatureIndex].situation.position, game.Conf.MaxInteractionDistance)

    raise NotImplementedError(f"Action {action} not implemented.")

def closeTo(pos1: Point, pos2: Point, maxDistance: int) -> bool:
    return bool(np.linalg.norm(np.array(pos1.AsTuple()) - np.array(pos2.AsTuple())) < maxDistance)

def findClosestCreatureIndex(game: Game, creatureIndex: int) -> int:
    creature = game.State.Creatures[creatureIndex]

    return int(np.argmin([
        np.linalg.norm(np.array(creature.situation.position.AsTuple()) - np.array(game.State.Creatures[i].situation.position.AsTuple()))
        for i in range(len(game.State.Creatures))
        if i != creatureIndex
    ]))

def findClosestResourceIndex(game: Game, creatureIndex: int) -> int:
    creaturePos = game.State.Creatures[creatureIndex].situation.position.AsTuple()

    return int(np.argmin([
        np.linalg.norm(np.array(creaturePos) - np.array(resource.position.AsTuple()))
        for resource in game.State.Resources
    ]))
    
def noOverlap(game: Game, point: Point) -> bool:
    return not any([
        c.situation.position.x == point.x and c.situation.position.y == point.y
        for c in game.State.Creatures
    ])

def getNextActionBasedOnGenomeRandomly(game: Game, creatureIndex: int) -> Action.Action:
    creature = game.State.Creatures[creatureIndex]
    options = range(1, len(Action.Action) +1)
    actionIndex = int(np.random.choice(options, p=creature.base.genome.genes / creature.base.genome.genes.sum()))
    return Action.Action(actionIndex)

def executeAllActions(game: Game):

    creaturesToRemove = []

    for i, creature in enumerate(game.State.Creatures):

        ambiguousActionObject = game.Logic.DecisionFn(game, i)
        action = None
        if game.Conf.DecisionFnType == DecisionFnType.GetOneAction: 
            action = ambiguousActionObject

            while not IsActionValid(game, i, action):
                action = game.Logic.DecisionFn(game, i)
        elif game.Conf.DecisionFnType == DecisionFnType.GetAllActionsSorted:
            i = 0
            while not IsActionValid(game, i, ambiguousActionObject[i]):
                i += 1
                
            action = ambiguousActionObject[i]

        creature.actionDescriptions.append(str(action))
        
        if action == Action.Action.Stay:
            pass

        elif action == Action.Action.Consume:
            resourceIndex = findClosestResourceIndex(game, i)
            resource = game.State.Resources[resourceIndex]

            if closeTo(game.State.Creatures[i].situation.position, resource.position, game.Conf.MaxConsumptionDistance):
                game.State.Creatures[i].situation.resources = ResourceUtil.clampResource(game, game.State.Creatures[i].situation.resources + resource.containedResources)
                game.State.Resources.pop(resourceIndex)
            
        elif action == Action.Action.Produce:
            # drop a resource

            game.State.Resources.append(
                Resource.Resource(
                    hash=random.randint(0, 1_000_000_000),
                    position=creature.situation.position,
                    containedResources=creature.situation.resources / game.Conf.ProductionDivisor
                )
            )

            creature.situation.resources /= game.Conf.ProductionDivisor

        elif action == Action.Action.Die:
            creaturesToRemove.append(i)

            if game.RunningConfig.Debug:
                print('Creature ' + str(i) + ' commited suicide.')

        elif action == Action.Action.Reproduce:
            game.State.Creatures.append(
                game.Logic.BornCreatureFn(game, creature)
            )

            otherCreatureIndex = len(game.State.Creatures)-1

            game = exchangeResources(game, i, otherCreatureIndex, game.Conf.ReproductiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Reproduction of ' + str(i))

        elif action == Action.Action.MoveLeft:
            game.State.Creatures[i].situation.position.x -= game.Conf.CreatureStepSize
        elif action == Action.Action.MoveRight:
            game.State.Creatures[i].situation.position.x += game.Conf.CreatureStepSize
        elif action == Action.Action.MoveUp:
            game.State.Creatures[i].situation.position.y -= game.Conf.CreatureStepSize
        elif action == Action.Action.MoveDown:
            game.State.Creatures[i].situation.position.y += game.Conf.CreatureStepSize

        elif action == Action.Action.NeutralExchange:
            otherCreatureIndex = findClosestCreatureIndex(game, i)
            game = exchangeResources(game, i, otherCreatureIndex, 2)

            if game.RunningConfig.Debug:
                print('Neutral exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.ConstructiveExchange:
            otherCreatureIndex = findClosestCreatureIndex(game, i)
            game = exchangeResources(game, i, otherCreatureIndex, game.Conf.ConstructiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Constructive exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.DestructiveExchange:
            otherCreatureIndex = findClosestCreatureIndex(game, i)
            
            shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources
            shared_resources /= game.Conf.WinnerGetsAllDivisor

            winner = random.choice([i, otherCreatureIndex])
            loser = i if winner == otherCreatureIndex else otherCreatureIndex

            game.State.Creatures[winner].situation.resources = ResourceUtil.clampResource(game, shared_resources)
            game.State.Creatures[loser].situation.resources.fill(0)

            if game.RunningConfig.Debug:
                print('Destructive exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.LethalExchange:
            otherCreatureIndex = findClosestCreatureIndex(game, i)

            shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources
            shared_resources /= game.Conf.WinnerGetsAllDivisor

            winner = random.choice([i, otherCreatureIndex])
            loser = i if winner == otherCreatureIndex else otherCreatureIndex

            game.State.Creatures[winner].situation.resources = ResourceUtil.clampResource(game, shared_resources)
            creaturesToRemove.append(i)

            if game.RunningConfig.Debug:
                print('Lethal exchange between ' + str(i) + ' and ' + str(otherCreatureIndex) + '. Winner: ' + str(winner) + '. Loser: ' + str(loser))

        elif action == Action.Action.ReproduceBiparentally:
            otherCreatureIndex = findClosestCreatureIndex(game, i)

            shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources

            game.State.Creatures.append(
                game.Logic.BiparentalBornCreatureFn(game, game.State.Creatures[i], game.State.Creatures[otherCreatureIndex], shared_resources)
            )

            exchangeResources(game, i, otherCreatureIndex, game.Conf.BiparentalReproductiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Biparental reproduction between ' + str(i) + ' and ' + str(otherCreatureIndex))

        else:
            raise NotImplementedError('Unknown action: ' + str(action))
        
    game.State.Creatures = [
        c for i, c in enumerate(game.State.Creatures) if i not in creaturesToRemove
    ]
        
    return game

def removeCreatureByHash(game: Game, creatureHash: int):
    creatureIndex = findCreatureIndex(game, creatureHash)
    return game.State.Creatures.pop(creatureIndex)

def findCreatureIndex(game: Game, creatureHash) -> int:
    for i, creature in enumerate(game.State.Creatures):
        if creature.hash == creatureHash:
            return i
    raise ValueError('Creature not found: ' + str(creatureHash) + ' in ' + str(game.State.Creatures))

def exchangeResources(game, i, otherCreatureIndex, divisor) -> Game:
    shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources

    game.State.Creatures[i].situation.resources = ResourceUtil.clampResource(game, shared_resources / divisor)
    game.State.Creatures[otherCreatureIndex].situation.resources = ResourceUtil.clampResource(game, shared_resources / divisor)
    
    return game
