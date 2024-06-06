import itertools

from enum import Enum, auto
from pathlib import Path

import mip
import networkx as nx

from .model import Model

from src.utils import Colors


class Slitherlink(Model):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verifyData(self) -> None:
        for cell in self.data['nLinesSurround']:
            if (
                0 < cell['row'] or cell['row'] >= self.data['shape'][0]
                or 0 < cell['col'] or cell['col'] >= self.data['shape'][1]
            ):
                raise ValueError(f'Cell ({cell}) has invalid coordinate')
            if cell['val'] >= 4:
                raise ValueError(f'Cell ({cell}) has invalid value. Value must be less than 4')
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.xVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'x_{row}_{col}')
                for col in range(self.data['shape'][1])
            ]
            for row in range(self.data['shape'][0])
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addNumberLinesSurroundConstraints()
        return None

    def addNumberLinesSurroundConstraints(self) -> None:
        for cell in self.data['nLinesSurround']:
            surroundCells = [
                (cell['row'] + i, cell['col'] + j)
                for i, j in [(0, -1), (0, 1), (-1, 0), (1, 0)]
                if (
                    0 <= cell['row'] + i < self.data['shape'][0]
                    and 0 <= cell['col'] + j < self.data['shape'][1]
                )
            ]
            if cell['val'] == 0:
                self.addConstraint(
                    mip.xsum(
                        self.xVars[surroundCell[0]][surroundCell[1]]
                        for surroundCell in surroundCells
                    ) - 4*self.xVars[cell['row']][cell['col']] == 0
                )
            elif cell['val'] == 1:
                self.addConstraint(
                    mip.xsum(
                        self.xVars[surroundCell[0]][surroundCell[1]]
                        for surroundCell in surroundCells
                    ) - 2*self.xVars[cell['row']][cell['col']] == 1
                )
            elif cell['val'] == 2:
                self.addConstraint(
                    mip.xsum(
                        self.xVars[surroundCell[0]][surroundCell[1]]
                        for surroundCell in surroundCells
                    ) == 2
                )
            elif cell['val'] == 3:
                self.addConstraint(
                    mip.xsum(
                        self.xVars[surroundCell[0]][surroundCell[1]]
                        for surroundCell in surroundCells
                    ) + 2*self.xVars[cell['row']][cell['col']] == 3
                )
            else:
                raise ValueError(f'Cell ({cell}) has invalid value')
        return None

    def addConnectedConstraints(self) -> None:
        return None

    def visualize(self) -> None:
        super().visualize()
        nLinesSurroundCells = {
            (cell['row'], cell['col']): cell['val'] for cell in self.data['nLinesSurround']
        }
        for row in range(self.data['shape'][0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data['shape'][1]):
                if (row, col) in nLinesSurroundCells.keys():
                    renderRow += f' {Colors.BOLD}{Colors.GREEN}{nLinesSurroundCells[(row, col)]}{Colors.ENDC} '
                else:
                    if self.xVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.GREEN}⚝{Colors.ENDC} '
                    else:
                        renderRow += f'   '
                if col == self.data['shape'][1] - 1 or self.xVars[row][col].x != self.xVars[row][col + 1].x:
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    crossNode = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    renderRow += f' '
                    crossNode = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0 or self.xVars[row][col].x != self.xVars[row - 1][col].x:
                    normalCrossNode = f'{Colors.GRAY}+{Colors.ENDC}'
                    if renderUpRow.endswith(normalCrossNode):
                        renderUpRow = renderUpRow[:len(renderUpRow) - len(normalCrossNode)]
                        renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    renderUpRow += f'   {crossNode}'
            print(renderUpRow)
            print(renderRow)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data["shape"][1] + 1))}{Colors.ENDC}')
        return None
