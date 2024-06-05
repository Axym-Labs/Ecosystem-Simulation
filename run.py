
import numpy as np
import random
import matplotlib.pyplot as plt
from ecosystem import Action
from ecosystem import Creature
from ecosystem import Game
from ecosystem import Resource
from ecosystem import Base
from ecosystem import Genome
from ecosystem import GameRunner
from ecosystem import GameUtil

Conf = Game.GameConfiguration(
    MapDimensions=(80, 60),
    CreatureLimit=100,

    ResourceDensity=0.1,
    ResourceLength=3,
    MaxResourceValue=4.0,

    TileSize=10,
    MaxConsumptionDistance = 6,
    MaxInteractionDistance = 5,
    CreatureStepSize = 1,

    ConstructiveInteractionDivisor = 2.5,
    ProductionDivisor = 1.25,
    ReproductiveInteractionDivisor = 3,
    BiparentalReproductiveInteractionDivisor = 3,

    ResourceDepletionRate = 0.02,
    HealthDepletionRate = 0.05,
    HealthGainRate = 0.02,
    MaxHealth = 2.0,

    HashFn=lambda: np.random.randint(0, 1_000_000_000),
    ContainedResourceFn=lambda: np.ones(Conf.ResourceLength),

    DeathCondition=lambda game, i: game.State.Creatures[i].situation.health <= 0 or (game.State.Creatures[i].situation.age > 100 and random.random() < 0.1),
    TooFewResourcesFn=lambda game, i: game.State.Creatures[i].situation.resources.sum() < 1,

    ForceExitCondition=lambda game, frame: len(game.State.Creatures) == 0 or frame > 20_000
)

creatures = Creature.createCreaturesRandomly(
    20,
    Conf.MapDimensions,
    lambda: Creature.createOneCreature(
        Conf.HashFn(),
        Genome.GenomeScalar(np.random.rand(len(Action.Action))),
        Conf.ContainedResourceFn(),
        lambda: Base.Point(
            random.randint(0, Conf.MapDimensions[0]-1),
            random.randint(0, Conf.MapDimensions[1]-1)
        )
    ),
)

resources = Resource.createResourcesRandomly(
    50,
    Conf.MapDimensions, 
    lambda: Resource.createOneResource(
        Conf.HashFn(),
        Base.Point(
            x=random.randint(0, Conf.MapDimensions[0]-1),
            y=random.randint(0, Conf.MapDimensions[1]-1)
        ),
        Conf.ContainedResourceFn()
    )
)

game = Game.Game(
    Configuration=Conf,
    State=Game.GameState(
        Running = True,
        Creatures=creatures,
        Resources=resources,
    ),
    RunningConfig=Game.GameRunningConfig(
        Debug=False,
        PrintStats=True,
        SaveActions=True,
        SavePerformanceInfo=True
    )
)

gameRunner = GameRunner.GameRunner(game)
gameRunner.Run()


entrylen = len(gameRunner.actionDescriptions[next(iter(gameRunner.actionDescriptions.keys()))])

totalActionsOverTime = [
    sum([
        gameRunner.actionDescriptions[j][i][1]
        for j in range(1, len(Action.Action)+1)
    ]) for i in range(entrylen)
]

def plot_stuff():
    plt.clf()

    for i in range(1, len(Action.Action)+1):
        graph = [
            (gameRunner.actionDescriptions[i][j][0], gameRunner.actionDescriptions[i][j][1] / totalActionsOverTime[j]) for j in range(entrylen)
            if totalActionsOverTime[j] > 0
        ]

        plt.plot(graph, label=Action.Action(i))

    plt.legend()
    plt.savefig('data/actions.png')
    plt.show()

    plt.clf()

    for i, k in enumerate(gameRunner.performanceData.keys()):
        plt.plot(gameRunner.performanceData[k], label=k)

    plt.legend()
    plt.savefig('data/performance.png')
    plt.show()

plot_stuff()