
import numpy as np
import random
import matplotlib.pyplot as plt
from ecosystem import Action
from ecosystem import ActionNN
from ecosystem import Creature
from ecosystem import Game
from ecosystem import GameUtil
from ecosystem import Resource
from ecosystem import Base
from ecosystem import Genome
from ecosystem import GameRunner

DIMS = (40, 40)
focusPoints = Base.FocusPoint(DIMS, 4)
pointsIterator = Base.AllPointsIterator(DIMS, allowAfterEnd=True)

Conf = Game.GameConfiguration(
    FrameWaitTime=10,
    OtherOptions={
        # "DropResourcesOnDeath": False, # NOT IMPLEMENTED
        # "BlockInteraction": True, 
        # "BlockProduction": True,
        "AllowActionsExclusively": [Action.Action.Stay, Action.Action.MoveSomeWhere, Action.Action.Consume],
        "SpawnResources": {
            "ProbabilityPerFrame": 0.2
        },
        "SimpleNNModel-1": {
            "LookBlockRadius": 1,
        }
    },
    MapDimensions=DIMS,
    CreatureLimit=100,

    ResourceDensity=0.2,
    ResourceLength=3,
    MaxResourceValue=4.0,

    TileSize=20,
    MaxConsumptionDistance = 1,
    MaxInteractionDistance = 1,
    CreatureStepSize = 1,

    ConstructiveInteractionDivisor = 3,
    WinnerGetsAllDivisor = 1.75,
    ProductionDivisor = 2,
    ReproductiveInteractionDivisor = 4,
    BiparentalReproductiveInteractionDivisor = 4,

    ResourceDepletionRate = 0.02,
    HealthDepletionRate = 0.02,
    HealthGainRate = 0.04,
    MaxHealth = 2.0,

    DecisionFnType=Base.DecisionFnType.GetAllActionsSorted
)

Logic = Game.GameLogic(

    ForceExitCondition=lambda game, frame: len(game.State.Creatures) == 0 or frame > 20_000,
    HashFn=lambda: np.random.randint(0, 1_000_000_000),
    ContainedResourceFn=lambda: np.ones(Conf.ResourceLength),

    DeathCondition=lambda game, i: game.State.Creatures[i].situation.health <= 0 or (game.State.Creatures[i].situation.age > 50 and random.random() < 0.1),
    TooFewResourcesFn=lambda game, i: game.State.Creatures[i].situation.resources.sum() < 0,
    DecisionFn=lambda game, creatureIndex: ActionNN.getNextActionBasedOnNNModel(game, creatureIndex, []),

    BornCreatureFn=lambda game, parent: Creature.createOneCreature(
        hash=game.Logic.HashFn(),
        genome=parent.base.genome,
        resources=np.zeros(game.Conf.ResourceLength),
        position=Base.Point(parent.situation.position.x, parent.situation.position.y),
        health=0.5
    ),

    BiparentalBornCreatureFn=lambda game, parent1, parent2, shared_resources: Creature.createOneCreature(
        hash=game.Logic.HashFn(),
        genome=parent1.base.genome.combineWith(parent2.base.genome),
        resources=shared_resources / game.Conf.BiparentalReproductiveInteractionDivisor,
        position=Base.Point(parent1.situation.position.x, parent1.situation.position.y),
        health=0.5
    ),

    CreateResourceFn=lambda conf, logic: Resource.createOneResource(
        hash=logic.HashFn(),
        # position=Base.randomPointWithBias(conf.MapDimensions, focusPoints.getOne(), 2.5),
        position=pointsIterator.__next__(), 
        resourceDistribution=logic.ContainedResourceFn()
    ),

    SummaryFn=GameUtil.printStats
)

CENTER_BIAS = 8

creatures = Creature.createCreaturesRandomly(
    200,
    Conf.MapDimensions,
    lambda: Creature.createOneCreature(
        Logic.HashFn(),
        Genome.NDGenome(
            # block radius one
            np.random.rand(112)
            # block radius two
            # np.random.rand(252)
        ),
        Logic.ContainedResourceFn(),
        Base.randomPointWithCenterBias(Conf.MapDimensions, CENTER_BIAS),
        0.1
    ),
)

RESOURCE_COUNT = DIMS[0] * DIMS[1] # 400

resources = Resource.createResourcesRandomly(
    RESOURCE_COUNT,
    Conf.MapDimensions, 
    lambda: Logic.CreateResourceFn(Conf, Logic),
)

game = Game.Game(
    Conf=Conf,
    Logic=Logic,
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

    graphsByFrame = []

    for i in range(1, len(Action.Action)+1):
        graphsByFrame.append([
            (gameRunner.actionDescriptions[i][j][0], gameRunner.actionDescriptions[i][j][1] / totalActionsOverTime[j]) for j in range(entrylen)
            if totalActionsOverTime[j] > 0
        ])

    graphsByFrameBatch = []

    for i, graph in enumerate(graphsByFrame):
        summed_graph = []
        for j in range(len(graph) - 10, len(graph)):
            summed_value = sum([graph[k][1] for k in range(j, len(graph))])
            summed_graph.append((graph[j][0], summed_value))
        graphsByFrameBatch.append(summed_graph)

    for i, graph in enumerate(graphsByFrameBatch):
        plt.plot([(x,y*10_000) for x,y in graph], label=str(Action.Action(i+1)).split(".")[1])

        with open(f'data/actions/{str(Action.Action(i+1)).split(".")[1]}.csv', 'w', encoding="utf-8") as f:
            for x, y in graph:
                f.write(f"{x},{y}\n")

    plt.legend()
    plt.savefig('data/actions.png')
    plt.show()

    plt.clf()

    for i, k in enumerate(gameRunner.performanceData.keys()):
        plt.plot(gameRunner.performanceData[k], label=k)

    plt.legend()
    plt.savefig('data/performance.png')
    plt.show()

# plot_stuff()