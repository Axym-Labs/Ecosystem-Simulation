
**Game of life with extra steps**

A 2d python ecosystem simulation using PyGame
Based on creatures and resources
Genes of creatures determine the probability of actions taken (chosen randomly)

Actions
```py
    Stay = 1
    Consume = 2
    Produce = 3
    Die = 4
    Reproduce = 5

    # Directed Actions
    MoveUp = 6
    MoveDown = 7	
    MoveLeft = 8
    MoveRight = 9

    # Interactions
    NeutralExchange = 10
    ConstructiveExchange = 11
    DestructiveExchange = 12
    LethalExchange = 13
    ReproduceBiparentally = 14
```