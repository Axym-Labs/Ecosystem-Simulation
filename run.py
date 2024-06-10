
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

Conf = Game.GameConfiguration(
    MapDimensions=(80, 60),
    CreatureLimit=100,

    ResourceDensity=0.1,
    ResourceLength=3,
    MaxResourceValue=4.0,

    TileSize=10,
    MaxConsumptionDistance = 2,
    MaxInteractionDistance = 2,
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

    ForceExitCondition=lambda game, frame: len(game.State.Creatures) == 0 or frame > 20_0,

    BornCreatureFn=lambda game, parent: Creature.createOneCreature(
        hash=game.Configuration.HashFn(),
        genome=parent.base.genome,
        resources=parent.situation.resources / game.Configuration.ReproductiveInteractionDivisor,
        position=Base.Point(parent.situation.position.x, parent.situation.position.y)
    ),

    BiparentalBornCreatureFn=lambda game, parent1, parent2, shared_resources: Creature.createOneCreature(
        hash=game.Configuration.HashFn(),
        genome=parent1.base.genome.combineWith(parent2.base.genome),
        resources=shared_resources / game.Configuration.BiparentalReproductiveInteractionDivisor,
        position=Base.Point(parent1.situation.position.x, parent1.situation.position.y)
    )
)

CENTER_BIAS = 15

creatures = Creature.createCreaturesRandomly(
    20,
    Conf.MapDimensions,
    lambda: Creature.createOneCreature(
        Conf.HashFn(),
        Genome.GenomeScalar(np.random.rand(len(Action.Action))),
        Conf.ContainedResourceFn(),
        Base.randomPointWithCenterBias(Conf.MapDimensions, CENTER_BIAS),
    ),
)

resources = Resource.createResourcesRandomly(
    50,
    Conf.MapDimensions, 
    lambda: Resource.createOneResource(
        Conf.HashFn(),
        Base.randomPointWithCenterBias(Conf.MapDimensions, CENTER_BIAS),
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

    graphs = []

    for i in range(1, len(Action.Action)+1):
        graphs.append([
            (gameRunner.actionDescriptions[i][j][0], gameRunner.actionDescriptions[i][j][1] / totalActionsOverTime[j]) for j in range(entrylen)
            if totalActionsOverTime[j] > 0
        ])

    for i, graph in enumerate(graphs):
        plt.plot(graph, label=str(Action.Action(i+1)).split(".")[1])

        with open(f'data/actions/{str(Action.Action(i+1)).split(".")[1]}.csv', 'w') as f:
            for x, y in graph:
                f.write(f"{x},{y}\n")

    plt.legend()
    plt.savefig('data/actions.png')
    plt.show()

    plt.clf()

    for i, k in enumerate(gameRunner.performanceData.keys()):
        plt.plot(gameRunner.performanceData[k], label=k)

    # print(gameRunner.performanceData)

    plt.legend()
    plt.savefig('data/performance.png')
    plt.show()

plot_stuff()