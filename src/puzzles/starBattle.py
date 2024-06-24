import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class StarBattle(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verifyData(self) -> None:
        sortedData = sorted(sum(
            [
                [(cell['row'], cell['col']) for cell in cage]
                for cage in self.data.cages
            ], start=[]
        ))
        for index, (row, col) in enumerate(itertools.product(
            range(self.data.shape[0]), range(self.data.shape[1])
        )):
            if (row, col) != sortedData[index]:
                cell = {"row": row, "col": col}
                raise ValueError(f"Cell {cell} has a problem!")
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.xVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'x_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0])
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addNStarsEachRowConstraints()
        self.addNStarsEachColumnConstraints()
        self.addNStarsEachCageConstraints()
        self.addStarsNotBeAdjacentEachOtherConstraints()
        return None

    def addNStarsEachRowConstraints(self) -> None:
        for row in range(self.data.shape[0]):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for col in range(self.data.shape[1])) == self.data.nStars
            )
        return None

    def addNStarsEachColumnConstraints(self) -> None:
        for col in range(self.data.shape[1]):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for row in range(self.data.shape[0])) == self.data.nStars
            )
        return None

    def addNStarsEachCageConstraints(self) -> None:
        for cage in self.data.cages:
            self.addConstraint(
                mip.xsum(self.xVars[cell['row']][cell['col']] for cell in cage) == self.data.nStars
            )
        return None

    def addStarsNotBeAdjacentEachOtherConstraints(self) -> None:
        # The stars may not be adjacent to each other (not even diagonally).
        blocks = {}
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[1])):
            blocks[(row, col)] = []
            for gapRow, gapCol in itertools.product([-1, 0, 1], [-1, 0, 1]):
                if gapRow == 0 and gapCol == 0:
                    continue
                if 0 <= row + gapRow < self.data.shape[0] and 0 <= col + gapCol < self.data.shape[1]:
                    blocks[(row, col)].append((row + gapRow, col + gapCol))
        for cell, neighbors in blocks.items():
            nNeighborCells = len(neighbors)
            self.addConstraint(
                nNeighborCells * self.xVars[cell[0]][cell[1]]
                + mip.xsum(self.xVars[row][col] for row, col in neighbors)
                <= nNeighborCells
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        cages = [[None] * self.data.shape[1] for _ in range(self.data.shape[0])]
        for index, cage in enumerate(self.data.cages):
            for cell in cage:
                if cages[cell['row']][cell['col']] is not None:
                    raise ValueError(f'Cell {cell} is duplicated')
                cages[cell['row']][cell['col']] = index
        for row in range(self.data.shape[0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if self.xVars[row][col].x == 1:
                    renderRow += f' {Colors.BOLD}{Colors.GREEN}⚝{Colors.ENDC} '
                else:
                    renderRow += f'   '
                if col == self.data.shape[1] - 1 or cages[row][col] != cages[row][col + 1]:
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    crossNode = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    renderRow += f' '
                    crossNode = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0 or cages[row][col] != cages[row - 1][col]:
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
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}')
        return None
