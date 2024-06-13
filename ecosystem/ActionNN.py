import numpy as np
from ecosystem import Game
from ecosystem import Base
from ecosystem import Action

def encodeSurroundingEnvironment(game: Game.Game, creatureIndex: int, blockRadius: int) -> list[np.ndarray]:
    x_start, x_end, y_start, y_end = Base.MapBoundariesAroundPosition(game.Conf.MapDimensions, game.State.Creatures[creatureIndex].situation.position, blockRadius)

    cArr = np.ndarray((x_end - x_start +1, y_end - y_start +1))
    rArr = np.ndarray((x_end - x_start +1, y_end - y_start +1))

    toRelativeIndex = lambda point: (point.x-x_start, point.y-y_start)

    for c in game.State.Creatures:
        if c.situation.position.WithinRanges(x_start, x_end, y_start, y_end):
            cArr[toRelativeIndex(c.situation.position)] = 1

    for r in game.State.Resources:
        if r.position.WithinRanges(x_start, x_end, y_start, y_end):
            rArr[toRelativeIndex(r.position)] = 1

    return [cArr, rArr]

def getNextActionBasedOnNNModel(game: Game.Game, creatureIndex: int, hiddenLayers: list[int]) -> list[Action.Action]:
    "fully connected feed forward linear nn. genome must be a 1d array containing the weights of the model. the action is returned as an int"

    # TODO: , separateInputTypes: bool

    # action shouldnt be just an enum (instead less rigid), especially for movement, maybe for directed interaction too

    assert "SimpleNNModel-1" in game.Conf.OtherOptions
    assert "LookBlockRadius" in game.Conf.OtherOptions["SimpleNNModel-1"]

    lookRadius = game.Conf.OtherOptions["SimpleNNModel-1"]["LookBlockRadius"]

    # add input and output layers
    layers = [(lookRadius+1) ** 2, *hiddenLayers, len(Action.Action)]

    genome = game.State.Creatures[creatureIndex].base.genome.genes

    assert layers[0] == (lookRadius+1) ** 2, f"Input layer must have the same number of neurons as the blocks visibile to the creature: is {layers[0]}, should have been {(lookRadius+1) ** 2}"

    environmentArr = encodeSurroundingEnvironment(game, creatureIndex, lookRadius)

    # len(environmentArr): each data has its own nn, the results will be aggregated
    # sum(layers): each layer needs 
    expectedWeightCount = len(environmentArr) * sum([layers[i] * layers[i-1] for i in range(1, len(layers))])
    assert len(genome) == expectedWeightCount, f"The genome does not have the correct number of weights for the nn model: is {len(genome)}, should have been {expectedWeightCount}"

    output = np.zeros((len(Action.Action)))

    environmentArr = [data.flatten() for data in environmentArr][:1]

    for i, data in enumerate(environmentArr):
        
        start = (i+1) ** 2 * i

        for j, nodeCount in enumerate(layers):
            end = start + nodeCount * len(data)
            weights = genome[start:end]

            print(f"dot product between {', '.join([str(weights[k]) + ' and ' + str(len(data)) for k in range(nodeCount)])}")

            data = np.array([
                np.sum(np.dot(data, weights[k])) 
                for k in range(nodeCount)
            ])

            start = end

        output += data

    actionIndices = sorted([i for i in range(len(Action.Action))], reverse=True, key=lambda action: output[action.value-1])
    return [Action.Action(i) for i in actionIndices]