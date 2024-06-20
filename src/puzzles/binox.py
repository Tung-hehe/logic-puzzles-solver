import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Binox(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.verifyData()
        return None

    def verifyData(self) -> None:
        if self.data['shape'][0] % 2 == 1 or self.data['shape'][1] % 2 == 1:
            raise ValueError(f"Shape must be even, not {self.data['shape']}")
        for cell in self.data['fixed']:
            if (
                cell['row'] < 0 or cell['row'] >= self.data['shape'][0]
                or cell['col'] < 0 or cell['col'] >= self.data['shape'][1]
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data['shape']}.")
            if cell['val'] not in ['X', 'O']:
                raise ValueError(f"Fixed value in cell {cell} should be 'X' or 'O'.")
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
        self.yVars = {}
        for col in range(self.data['shape'][1]):
            for row1, row2 in itertools.combinations(range(self.data['shape'][0]), 2):
                self.yVars[(row1, row2, col)] = self.addVariable(
                    vtype=mip.BINARY, name=f'y_{row1}_{row2}_{col}'
                )
        self.zVars = {}
        for row in range(self.data['shape'][0]):
            for col1, col2 in itertools.combinations(range(self.data['shape'][1]), 2):
                self.zVars[(col1, col2, row)] = self.addVariable(
                    vtype=mip.BINARY, name=f'y_{row1}_{col2}_{row}'
                )
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addFixedCellConstraints()
        self.addNoMoreThanNSameSymbolTouchingInRowConstraints()
        self.addNoMoreThanNSameSymbolTouchingInColConstraints()
        self.addEqualNumberOfXsAndOsInEachRowConstraints()
        self.addEqualNumberOfXsAndOsInEachColConstraints()
        self.addUniqueRowConstraints()
        self.addUniqueColConstraints()
        return None

    def addNoMoreThanNSameSymbolTouchingInRowConstraints(self) -> None:
        for row in range(self.data['shape'][0]):
            for col in range(self.data['shape'][1] - self.data['nSymbols']):
                self.addConstraint(
                    mip.xsum(self.xVars[row][col + gap] for gap in range(self.data['nSymbols'] + 1)) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(self.xVars[row][col + gap] for gap in range(self.data['nSymbols'] + 1)) >= 1
                )
        return None

    def addNoMoreThanNSameSymbolTouchingInColConstraints(self) -> None:
        for col in range(self.data['shape'][1]):
            for row in range(self.data['shape'][0] - self.data['nSymbols']):
                self.addConstraint(
                    mip.xsum(self.xVars[row + gap][col] for gap in range(self.data['nSymbols'] + 1)) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(self.xVars[row + gap][col] for gap in range(self.data['nSymbols'] + 1)) >= 1
                )
        return None

    def addEqualNumberOfXsAndOsInEachRowConstraints(self) -> None:
        for row in range(self.data['shape'][0]):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for col in range(self.data['shape'][1])) == self.data['shape'][1] / 2
            )
        return None

    def addEqualNumberOfXsAndOsInEachColConstraints(self) -> None:
        for col in range(self.data['shape'][1]):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for row in range(self.data['shape'][0])) == self.data['shape'][0] / 2
            )
        return None

    def addFixedCellConstraints(self) -> None:
        for cell in self.data['fixed']:
            if cell['val'] == 'X':
                self.addConstraint(self.xVars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'O':
                self.addConstraint(self.xVars[cell['row']][cell['col']] == 0)
            else:
                raise ValueError(f"In valid value in cell {cell}")

    def addUniqueRowConstraints(self) -> None:
        for col in range(self.data['shape'][1]):
            for row1, row2 in itertools.combinations(range(self.data['shape'][0]), 2):
                self.addConstraint(
                    self.yVars[(row1, row2, col)] + self.xVars[row1][col] + self.xVars[row2][col] >= 1
                )
                self.addConstraint(
                    self.yVars[(row1, row2, col)] + self.xVars[row1][col] <= 1 + self.xVars[row2][col]
                )
                self.addConstraint(
                    self.yVars[(row1, row2, col)]  + self.xVars[row2][col] <= 1 + self.xVars[row1][col]
                )
                self.addConstraint(
                    self.xVars[row1][col] + self.xVars[row2][col] <= 1 + self.yVars[(row1, row2, col)]
                )
        for row1, row2 in itertools.combinations(range(self.data['shape'][0]), 2):
            self.addConstraint(
                mip.xsum(self.yVars[(row1, row2, col)] for col in range(self.data['shape'][1])) <= self.data['shape'][1] - 1
            )
        return None

    def addUniqueColConstraints(self) -> None:
        for row in range(self.data['shape'][0]):
            for col1, col2 in itertools.combinations(range(self.data['shape'][1]), 2):
                self.addConstraint(
                    self.zVars[(col1, col2, row)] + self.xVars[row][col1] + self.xVars[row][col2] >= 1
                )
                self.addConstraint(
                    self.zVars[(col1, col2, row)] + self.xVars[row][col1] <= 1 + self.xVars[row][col2]
                )
                self.addConstraint(
                    self.zVars[(col1, col2, row)]  + self.xVars[row][col2] <= 1 + self.xVars[row][col1]
                )
                self.addConstraint(
                    self.xVars[row][col1] + self.xVars[row][col2] <= 1 + self.zVars[(col1, col2, row)]
                )
        for col1, col2 in itertools.combinations(range(self.data['shape'][1]), 2):
            self.addConstraint(
                mip.xsum(self.zVars[(col1, col2, row)] for row in range(self.data['shape'][0])) <= self.data['shape'][0] - 1
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixCells = [(cell['row'], cell['col']) for cell in self.data['fixed']]
        for row in range(self.data['shape'][0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data['shape'][1]):
                if (row, col) in fixCells:
                    if self.xVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.GRAY}X{Colors.ENDC} '
                    else:
                        renderRow += f' {Colors.BOLD}{Colors.GRAY}O{Colors.ENDC} '
                else:
                    if self.xVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.RED}X{Colors.ENDC} '
                    else:
                        renderRow += f' {Colors.BOLD}{Colors.BLUE}O{Colors.ENDC} '
                if col == self.data['shape'][1] - 1:
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    renderRow += f'{Colors.GRAY}|{Colors.ENDC}'
                    node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0:
                    renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    renderUpRow += f'{Colors.GRAY}---{Colors.ENDC}{node}'
            print(renderUpRow)
            print(renderRow)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data["shape"][1] + 1))}{Colors.ENDC}')
        return None
