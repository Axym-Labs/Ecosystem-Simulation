
import pygame
import random
from pygame import Surface
from ecosystem.Game import Game
from ecosystem.Resource import Resource
from ecosystem.Base import *

def render(game: Game, screen: Surface):
    for resource in game.State.Resources:
        mid = resource.position.AsTupleOfFloats()
        coords = [
            int(mid[0] * game.Conf.TileSize), 
            int(mid[1] * game.Conf.TileSize),
            game.Conf.TileSize,
            game.Conf.TileSize
        ]
        pygame.draw.rect(screen, getResourceColor(resource, game.Conf.ResourceLength), coords)

def getResourceColor(resource: Resource, resourceLength: int) -> tuple[int, int, int]:
    col = (
        0,
        0,
        clampToInt(255 * resource.containedResources.sum() / resourceLength, 0, 255)
    )
    return col

def spawnResources(game: Game):
    if random.random() < game.Conf.OtherOptions["SpawnResources"]["ProbabilityPerFrame"]:
        game.State.Resources.append(game.Logic.CreateResourceFn(game.Conf, game.Logic))

def clampResource(game: Game, resource):
    return np.clip(resource, 0, game.Conf.MaxResourceValue)

