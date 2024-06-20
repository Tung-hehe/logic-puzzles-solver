import itertools

from enum import Enum
from pathlib import Path

import mip
import networkx as nx


from src.model import BaseModel
from src.utils import Colors


class Mirror(Enum):
    TopLeftToRightDown = '\\'
    TopRightToLeftDown = '/'


class Direction(Enum):
    Top = 'top'
    Down = 'down'
    Left = 'left'
    Right = 'right'


class HauntedMirrorMaze(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.changeDirection = {
            (Direction.Top, Mirror.TopLeftToRightDown): Direction.Right,
            (Direction.Top, Mirror.TopRightToLeftDown): Direction.Left,
            (Direction.Down, Mirror.TopLeftToRightDown): Direction.Left,
            (Direction.Down, Mirror.TopRightToLeftDown): Direction.Right,
            (Direction.Left, Mirror.TopLeftToRightDown): Direction.Down,
            (Direction.Left, Mirror.TopRightToLeftDown): Direction.Up,
            (Direction.Right, Mirror.TopLeftToRightDown): Direction.Up,
            (Direction.Right, Mirror.TopRightToLeftDown): Direction.Down,
        }
        return None

    def verifyData(self) -> None:
        return None

    def convertData(self) -> None:
        return None

    def findVisibleCells(self) -> None:
        return None
