from enum import Enum


# USe for HauntedMirrorMaze
class Mirror(Enum):
    LeftDownToRight = '\\'
    RightDownToLeft = '/'

# USe for HauntedMirrorMaze
class Position(Enum):
    Top = 'top'
    Bottom = 'bottom'
    Left = 'left'
    Right = 'right'

# USe for HauntedMirrorMaze
class Monster(Enum):
    Vampire = 'V'
    Ghost = 'G'
    Zombie = 'Z'
