import pygame
from pygame import Surface
from ecosystem.Game import Game
from ecosystem.Creature import Creature
from ecosystem.Base import *

def render(game: Game, screen: Surface):
    for creature in game.State.Creatures:
        mid = creature.situation.position.AsTupleOfFloats()
        coords = [
            int(mid[0] * game.Conf.TileSize), 
            int(mid[1] * game.Conf.TileSize),
            game.Conf.TileSize,
            game.Conf.TileSize
        ]
        pygame.draw.rect(screen, getCreatureColor(game, creature, game.Conf.ResourceLength), coords)

def getCreatureColor(game: Game, creature: Creature, resourceLength: int) -> tuple[int, int, int]:
    # may be larger than 1, so we need to clamp it
    return (
        clampToInt(255 * creature.situation.health / game.Conf.MaxHealth, 0, 255),
        clampToInt(255 * creature.situation.age / 100, 0, 255),
        clampToInt(255 * creature.situation.resources.sum() / resourceLength / game.Conf.MaxResourceValue, 0, 255)
    )

def incrementAge(game: Game):
    for creature in game.State.Creatures:
        creature.situation.age += 1

    return game

def depleteResources(game: Game):
    for creature in game.State.Creatures:
        creature.situation.resources -= game.Conf.ResourceDepletionRate

    return game

def updateHealth(game: Game):
    for i, creature in enumerate(game.State.Creatures):
        if game.Logic.TooFewResourcesFn(game, i):
            creature.situation.health -= game.Conf.HealthDepletionRate
        elif creature.situation.health < game.Conf.MaxHealth:
            creature.situation.health += game.Conf.HealthGainRate

    return game

def removeDeadCreatures(game: Game):
    game.State.Creatures = [creature for i, creature in enumerate(game.State.Creatures) if not game.Logic.DeathCondition(game, i)]

    return game
