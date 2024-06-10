import pygame
from ecosystem.Game import Game
from typing import Callable
import time
from ecosystem import ResourceUtil
from ecosystem import CreatureUtil
from ecosystem.Creature import Creature
from ecosystem import Base
from ecosystem import Action
from ecosystem import ActionUtil
from ecosystem import GameUtil



class GameRunner():
    game: Game

    screen: pygame.Surface
    clock: pygame.time.Clock
    frame: int = 0
    actionDescriptions: dict[int, list[tuple[int, int]]]
    performanceData: dict[str, list[tuple[int, float]]]

    lastCreatures: list[Creature]

    def __init__(self, game: Game):
        self.game = game

        self.actionDescriptions = {}
        self.performanceData = {}
        self.lastCreatures = []

        pygame.init()
        pygame.display.set_caption('Ecosystem')
        
        screenDim = (
            self.game.Configuration.MapDimensions[0] * self.game.Configuration.TileSize, 
            self.game.Configuration.MapDimensions[1] * self.game.Configuration.TileSize
        )
        self.screen = pygame.display.set_mode(screenDim)
        self.clock = pygame.time.Clock()

    def Run(self):
        while self.game.State.Running:
            self.Update()

        if self.game.RunningConfig.PrintStats:
            GameUtil.printWinnerInfo(self.game, self.frame, self.lastCreatures)

        if self.game.RunningConfig.OnEnd != None:
            self.game.RunningConfig.OnEnd(self.game)

    def Update(self):
        self.frame += 1

        # print(f'Frame: {self.frame}')

        self.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.State.Running = False

        self.screen.fill((0, 0, 0))

        self.executeInnerGameFn(lambda: CreatureUtil.incrementAge(self.game), 'incrementAge', True)
        self.executeInnerGameFn(lambda: CreatureUtil.depleteResources(self.game), 'depleteResources', True)
        self.executeInnerGameFn(lambda: CreatureUtil.updateHealth(self.game), 'updateHealth', True)
        self.executeInnerGameFn(lambda: CreatureUtil.removeDeadCreatures(self.game), 'removeDeadCreatures', True)

        self.executeInnerGameFn(lambda: ActionUtil.executeAllActions(self.game, ActionUtil.getNextActionBasedOnGenome), 'executeAllActions', True)

        self.executeInnerGameFn(lambda: ResourceUtil.render(self.game, self.screen), 'renderResources', False)
        self.executeInnerGameFn(lambda: CreatureUtil.render(self.game, self.screen), 'renderCreatures', False)

        pygame.display.flip()

        if self.frame % 100 == 0 and self.game.RunningConfig.PrintStats:
            GameUtil.printStats(self.game, self.frame, self.lastCreatures)

        for i in range(1, len(Action.Action)+1):
            if i not in self.actionDescriptions:
                self.actionDescriptions[i] = []

            self.actionDescriptions[i].append(
                (
                    self.frame, 
                    len([c for c in self.game.State.Creatures if Base.safeCond(c, lambda c: c.actionDescriptions[-1] == str(Action.Action(i)))])
                )
            )

        if not self.game.Configuration.ForceExitCondition(self.game, self.frame):
            self.lastCreatures = self.game.State.Creatures
        else:
            self.game.State.Running = False
        

    def __del__(self):
        pygame.quit()

    def executeInnerGameFn(self, fn: Callable, description: str, set: bool):
        if not self.game.RunningConfig.SavePerformanceInfo:
            if set:
                self.game = fn()
            else:
                fn()
        else:
            start = time.perf_counter()

            if set:
                self.game = fn()
            else:
                fn()

            end = time.perf_counter()
            
            if description not in self.performanceData:
                self.performanceData[description] = []

            self.performanceData[description].append((self.frame, (end - start) * 1000))
