import functools
from ecosystem.Game import Game
from ecosystem.Creature import Creature
from ecosystem import Action

def printStats(game: Game, frame: int, lastCreatures: list[Creature]):
    print('Frame: ' + str(frame))
    print('Creatures: ' + str(len(lastCreatures)))
    # print('Resources: ' + str(len(game.State.Resources)))
    
    # if len(lastCreatures) > 0:
    #     print("Average Creature Resources: " + str(sum([c.situation.resources for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Creature Health: " + str(sum([c.situation.health for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Creature Age: " + str(sum([c.situation.age for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Resource Distribution: " + str(sum([r.containedResources for r in game.State.Resources]) / len(game.State.Resources)))
    # else:
    #     print("No creatures left to display info of.")

    if len(lastCreatures) > 0:
        print("Average genome")

        for i in range(len(Action.Action)):
            print(f"Gene {i} (Action {Action.Action(i+1)}): {sum([c.base.genome.genes[i] for c in lastCreatures]) / len(lastCreatures)}")

    print("-" * 20)


def printWinnerInfo(game: Game, frame: int, lastCreatures: list[Creature]):
    winners = ', '.join([str(c.hash) for c in lastCreatures])

    print(f"Creatures {winners} won!")
    lastCreatures.sort(key=lambda c: c.situation.resources.sum(), reverse=True)

    for c in lastCreatures[:10]:
        print(f"Creature {c.hash} ({c.situation.position.x}, {c.situation.position.y}) had {c.situation.resources} resources, {c.situation.health} health, and {c.situation.age} age.")
        # print("Moves made: " + ', '.join([str(a) for a in c.actionDescriptions]))
        
    printStats(game, frame, lastCreatures)

def printPositions(creatures: list[Creature]):
    maxX = max([c.situation.position.x for c in creatures])
    maxY = max([c.situation.position.y for c in creatures])
    print(f"Max X: {maxX}, Max Y: {maxY}")