import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Sudoku(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.modifiedFixedCellsValues()
        return None

    def verifyData(self) -> None:
        self.blockShape = int(self.data.shape ** 0.5)
        if self.blockShape ** 2 != self.data.shape:
            raise ValueError(f"Invalid shape")
        for cell in self.data.fixedCells:
            if (
                cell['row'] < 0 or cell['row'] >= self.data.shape
                or cell['col'] < 0 or cell['col'] >= self.data.shape
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data.shape}.")
            if cell['val'] > self.data.shape:
                raise ValueError(f"Fixed value in cell {cell} should be in range [1, {self.data.shape}].")
        return None

    def modifiedFixedCellsValues(self):
        for i in range(len(self.data.fixedCells)):
            self.data.fixedCells[i]['val'] = self.data.fixedCells[i]['val'] - 1
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.xVars = [
            [
                [
                    self.addVariable(vtype=mip.BINARY, name=f'x_{row}_{col}_{val}')
                    for val in range(self.data.shape)
                ]
                for col in range(self.data.shape)
            ]
            for row in range(self.data.shape)
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addFixedCellConstraints()
        self.addEachCellContainOneValueContraints()
        self.addUniqueNumberEachRowConstraints()
        self.addUniqueNumberEachColumnConstraints()
        self.addUniqueNumberEachBlockConstraints()
        return None

    def addEachCellContainOneValueContraints(self) -> None:
        for row, col in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.addConstraint(
                mip.xsum(self.xVars[row][col][val] for val in range(self.data.shape)) == 1
            )
        return None

    def addFixedCellConstraints(self) -> None:
        for cell in self.data.fixedCells:
            self.addConstraint(self.xVars[cell['row']][cell['col']][cell['val']] == 1)
        return None

    def addUniqueNumberEachRowConstraints(self) -> None:
        for row, val in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.addConstraint(
                mip.xsum(self.xVars[row][col][val] for col in range(self.data.shape)) == 1
            )
        return None

    def addUniqueNumberEachColumnConstraints(self) -> None:
        for col, val in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.addConstraint(
                mip.xsum(self.xVars[row][col][val] for row in range(self.data.shape)) == 1
            )
        return None

    def addUniqueNumberEachBlockConstraints(self) -> None:
        for row, col in itertools.product(
            range(0, self.data.shape, self.blockShape), range(0, self.data.shape, self.blockShape)
        ):
            for val in range(self.data.shape):
                self.addConstraint(
                    mip.xsum(
                        self.xVars[row + stepRow][col + stepCol][val]
                        for stepRow, stepCol in itertools.product(
                            range(self.blockShape), range(self.blockShape)
                        )
                    ) == 1
                )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixCells = {(cell['row'], cell['col']): cell['val'] for cell in self.data.fixedCells}
        for row in range(self.data.shape):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape):
                if (row, col) in fixCells.keys():
                    renderRow += f' {Colors.BOLD}{Colors.GRAY}{fixCells[(row, col)]}{Colors.ENDC} '
                else:
                    value = int(sum(val * self.xVars[row][col][val].x for val in range(self.data.shape)))
                    renderRow += f' {Colors.BOLD}{Colors.BLUE}{value + 1}{Colors.ENDC} '
                if (col + 1) % self.blockShape == 0:
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    renderRow += f'{Colors.GRAY}|{Colors.ENDC}'
                    node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row % self.blockShape == 0:
                    renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    renderUpRow += f'{Colors.GRAY}---{Colors.ENDC}{node}'
            print(renderUpRow)
            print(renderRow)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape + 1))}{Colors.ENDC}')
        return None
