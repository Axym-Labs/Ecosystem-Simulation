from ecosystem.Game import Game
from ecosystem.Creature import Creature

def printStats(game: Game, frame: int, lastCreatures: list[Creature]):
    print('Frame: ' + str(frame))
    print('Creatures: ' + str(len(lastCreatures)))
    print('Resources: ' + str(len(game.State.Resources)))

    # if len(lastCreatures) > 0:
    #     print("Average Creature Resources: " + str(sum([c.situation.resources for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Creature Health: " + str(sum([c.situation.health for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Creature Age: " + str(sum([c.situation.age for c in lastCreatures]) / len(lastCreatures)))
    #     print("Average Resource Distribution: " + str(sum([r.containedResources for r in game.State.Resources]) / len(game.State.Resources)))
    # else:
    #     print("No creatures left to display info of.")

    print("Average creature stats:")
    print("    Health: " + str(sum([c.situation.health for c in lastCreatures]) / len(lastCreatures)))
    print("    Age: "  + str(sum([c.situation.health for c in lastCreatures]) / len(lastCreatures)))
    print("    Resources: " + str(sum([c.situation.resources.sum() for c in lastCreatures]) / len(lastCreatures)))


    #  TODO fix this: action is empty but c.actionDescriptions is not
    actions = []
    for c in lastCreatures:
        actions += c.actionDescriptions[:-50]

    actionsByCount = {
        a: actions.count(a) for a in set(actions)
    }

    print("Actions by frequency (50 last frames)")

    for k, v in actionsByCount.items():
        print(f"{k}: {v}")

    print("-" * 30)


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