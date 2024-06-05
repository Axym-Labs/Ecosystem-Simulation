import pygame
from pygame import Surface
from typing import Callable
import random
import numpy as np
from ecosystem.Game import Game
from ecosystem.Creature import Creature, createOneCreature
from ecosystem import Action
from ecosystem import Action
from ecosystem import Resource
from ecosystem.Base import *

def render(game: Game, screen: Surface):
    for creature in game.State.Creatures:
        mid = creature.situation.position.AsTupleOfFloats()
        coords = [
            int(mid[0] * game.Configuration.TileSize), 
            int(mid[1] * game.Configuration.TileSize),
            game.Configuration.TileSize,
            game.Configuration.TileSize
        ]
        pygame.draw.rect(screen, getCreatureColor(game, creature, game.Configuration.ResourceLength), coords)

def getCreatureColor(game: Game, creature: Creature, resourceLength: int) -> tuple[int, int, int]:
    # may be larger than 1, so we need to clamp it
    return (
        clampToInt(255 * creature.situation.health / game.Configuration.MaxHealth, 0, 255),
        clampToInt(255 * creature.situation.age / 100, 0, 255),
        clampToInt(255 * creature.situation.resources.sum() / resourceLength / game.Configuration.MaxResourceValue, 0, 255)
    )

def incrementAge(game: Game):
    for creature in game.State.Creatures:
        creature.situation.age += 1

    return game

def depleteResources(game: Game):
    for creature in game.State.Creatures:
        creature.situation.resources -= game.Configuration.ResourceDepletionRate

    return game

def updateHealth(game: Game):
    for i, creature in enumerate(game.State.Creatures):
        if game.Configuration.TooFewResourcesFn(game, i):
            creature.situation.health -= game.Configuration.HealthDepletionRate
        elif creature.situation.health < game.Configuration.MaxHealth:
            creature.situation.health += game.Configuration.HealthGainRate

    return game

def removeDeadCreatures(game: Game):
    game.State.Creatures = [creature for i, creature in enumerate(game.State.Creatures) if not game.Configuration.DeathCondition(game, i)]

    return game


def getNextActionBasedOnGenome(game: Game, creatureIndex: int) -> Action.Action:
    creature = game.State.Creatures[creatureIndex]
    options = range(1, len(Action.Action) +1)
    actionIndex = int(np.random.choice(options, p=creature.base.genome.genes / creature.base.genome.genes.sum()))
    return Action.Action(actionIndex)



def executeAllActions(game: Game, decisionFn: Callable):

    creaturesToRemove = []

    for i, creature in enumerate(game.State.Creatures):
        action = decisionFn(game, i)

        while not Action.IsActionValid(game, i, action):
            action = decisionFn(game, i)

        creature.actionDescriptions.append(str(action))
        
        if action == Action.Action.Stay:
            pass

        elif action == Action.Action.Consume:
            resourceIndex = Action.findClosestResourceIndex(game, i)
            resource = game.State.Resources[resourceIndex]

            if Action.closeTo(game.State.Creatures[i].situation.position, resource.position, game.Configuration.MaxConsumptionDistance):
                game.State.Creatures[i].situation.resources = clampResource(game, game.State.Creatures[i].situation.resources + resource.containedResources)
                game.State.Resources.pop(resourceIndex)
            
        elif action == Action.Action.Produce:
            # drop a resource

            game.State.Resources.append(
                Resource.Resource(
                    hash=random.randint(0, 1_000_000_000),
                    position=creature.situation.position,
                    containedResources=creature.situation.resources / game.Configuration.ProductionDivisor
                )
            )

            creature.situation.resources /= game.Configuration.ProductionDivisor

        elif action == Action.Action.Die:
            creaturesToRemove.append(i)

            if game.RunningConfig.Debug:
                print('Creature ' + str(i) + ' commited suicide.')

        elif action == Action.Action.Reproduce:
            game.State.Creatures.append(
                createOneCreature(
                    hash=game.Configuration.HashFn(),
                    genome=creature.base.genome,
                    resources=creature.situation.resources / game.Configuration.ReproductiveInteractionDivisor,
                    positionFn=lambda: Point(creature.situation.position.x, creature.situation.position.y)
                )
            )

            otherCreatureIndex = len(game.State.Creatures)-1

            game = exchangeResources(game, i, otherCreatureIndex, game.Configuration.ReproductiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Reproduction of ' + str(i))

        elif action == Action.Action.MoveLeft:
            game.State.Creatures[i].situation.position.x -= game.Configuration.CreatureStepSize
        elif action == Action.Action.MoveRight:
            game.State.Creatures[i].situation.position.x += game.Configuration.CreatureStepSize
        elif action == Action.Action.MoveUp:
            game.State.Creatures[i].situation.position.y -= game.Configuration.CreatureStepSize
        elif action == Action.Action.MoveDown:
            game.State.Creatures[i].situation.position.y += game.Configuration.CreatureStepSize

        elif action == Action.Action.NeutralExchange:
            otherCreatureIndex = Action.findClosestCreatureIndex(game, i)
            game = exchangeResources(game, i, otherCreatureIndex, 2)

            if game.RunningConfig.Debug:
                print('Neutral exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.ConstructiveExchange:
            otherCreatureIndex = Action.findClosestCreatureIndex(game, i)
            game = exchangeResources(game, i, otherCreatureIndex, game.Configuration.ConstructiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Constructive exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.DestructiveExchange:
            otherCreatureIndex = Action.findClosestCreatureIndex(game, i)
            game = exchangeResources(game, i, otherCreatureIndex, 2 - game.Configuration.ConstructiveInteractionDivisor)

            if game.RunningConfig.Debug:
                print('Destructive exchange between ' + str(i) + ' and ' + str(otherCreatureIndex))

        elif action == Action.Action.LethalExchange:
            otherCreatureIndex = Action.findClosestCreatureIndex(game, i)

            shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources

            winner = random.choice([i, otherCreatureIndex])
            loser = i if winner == otherCreatureIndex else otherCreatureIndex

            dead = i == loser

            game.State.Creatures[winner].situation.resources = clampResource(game, shared_resources)
            creaturesToRemove.append(i)

            if game.RunningConfig.Debug:
                print('Lethal exchange between ' + str(i) + ' and ' + str(otherCreatureIndex) + '. Winner: ' + str(winner) + '. Loser: ' + str(loser))

        elif action == Action.Action.ReproduceBiparentally:
            otherCreatureIndex = Action.findClosestCreatureIndex(game, i)

            shared_resources = game.State.Creatures[i].situation.resources + game.State.Creatures[otherCreatureIndex].situation.resources

            game.State.Creatures.append(
                createOneCreature(
                    hash=game.Configuration.HashFn(),
                    genome=creature.base.genome.combineWith(game.State.Creatures[otherCreatureIndex].base.genome),
                    resources=shared_resources / game.Configuration.BiparentalReproductiveInteractionDivisor,
                    positionFn=lambda: Point(creature.situation.position.x, creature.situation.position.y)
                )
            )

            exchangeResources(game, i, otherCreatureIndex, game.Configuration.BiparentalReproductiveInteractionDivisor)

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

    game.State.Creatures[i].situation.resources = clampResource(game, shared_resources / divisor)
    game.State.Creatures[otherCreatureIndex].situation.resources = clampResource(game, shared_resources / divisor)
    
    return game

def clampResource(game: Game, resource):
    return np.clip(resource, 0, game.Configuration.MaxResourceValue)