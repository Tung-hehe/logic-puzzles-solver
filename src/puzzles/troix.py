import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Troix(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verifyData(self) -> None:
        if self.data['shape'][0] % 3 != 0 or self.data['shape'][1] % 3 != 0:
            raise ValueError(f"Shape mod 3 must be equal 0, not {self.data['shape']}")
        for cell in self.data['fixed']:
            if (
                cell['row'] < 0 or cell['row'] >= self.data['shape'][0]
                or cell['col'] < 0 or cell['col'] >= self.data['shape'][1]
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data['shape']}.")
            if cell['val'] not in ['X', 'O', 'I']:
                raise ValueError(f"Fixed value in cell {cell} should be 'X' or 'O'.")
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.XVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'X_{row}_{col}')
                for col in range(self.data['shape'][1])
            ]
            for row in range(self.data['shape'][0])
        ]
        self.OVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'O_{row}_{col}')
                for col in range(self.data['shape'][1])
            ]
            for row in range(self.data['shape'][0])
        ]
        self.IVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'I_{row}_{col}')
                for col in range(self.data['shape'][1])
            ]
            for row in range(self.data['shape'][0])
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addEachCellContaintOneSymbol()
        self.addFixedCellConstraints()
        self.addNoMoreThanNSameSymbolTouchingInRowConstraints()
        self.addNoMoreThanNSameSymbolTouchingInColConstraints()
        self.addEqualNumberOfXsAndOsAndIsInEachRowConstraints()
        self.addEqualNumberOfXsAndOsAndIsInEachColConstraints()
        return None

    def addEachCellContaintOneSymbol(self) -> None:
        for row, col in itertools.product(range(self.data['shape'][0]), range(self.data['shape'][0])):
            self.addConstraint(
                self.XVars[row][col] + self.OVars[row][col] + self.IVars[row][col] == 1
            )

    def addFixedCellConstraints(self) -> None:
        for cell in self.data['fixed']:
            if cell['val'] == 'X':
                self.addConstraint(self.XVars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'O':
                self.addConstraint(self.OVars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'I':
                self.addConstraint(self.IVars[cell['row']][cell['col']] == 1)
            else:
                raise ValueError(f"In valid value in cell {cell}")

    def addNoMoreThanNSameSymbolTouchingInRowConstraints(self) -> None:
        for row in range(self.data['shape'][0]):
            for col in range(self.data['shape'][1] - self.data['nSymbols']):
                self.addConstraint(
                    mip.xsum(
                        self.XVars[row][col + gap] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(
                        self.OVars[row][col + gap] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(
                        self.IVars[row][col + gap] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
        return None

    def addNoMoreThanNSameSymbolTouchingInColConstraints(self) -> None:
        for col in range(self.data['shape'][1]):
            for row in range(self.data['shape'][0] - self.data['nSymbols']):
                self.addConstraint(
                    mip.xsum(
                        self.XVars[row + gap][col] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(
                        self.OVars[row + gap][col] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
                self.addConstraint(
                    mip.xsum(
                        self.IVars[row + gap][col] for gap in range(self.data['nSymbols'] + 1)
                    ) <= self.data['nSymbols']
                )
        return None

    def addEqualNumberOfXsAndOsAndIsInEachRowConstraints(self) -> None:
        for row in range(self.data['shape'][0]):
            self.addConstraint(
                mip.xsum(
                    self.XVars[row][col] for col in range(self.data['shape'][1])
                ) == self.data['shape'][1] / 3
            )
            self.addConstraint(
                mip.xsum(
                    self.OVars[row][col] for col in range(self.data['shape'][1])
                ) == self.data['shape'][1] / 3
            )
            self.addConstraint(
                mip.xsum(
                    self.IVars[row][col] for col in range(self.data['shape'][1])
                ) == self.data['shape'][1] / 3
            )
        return None

    def addEqualNumberOfXsAndOsAndIsInEachColConstraints(self) -> None:
        for col in range(self.data['shape'][1]):
            self.addConstraint(
                mip.xsum(self.XVars[row][col] for row in range(self.data['shape'][0])) == self.data['shape'][0] / 3
            )
            self.addConstraint(
                mip.xsum(self.OVars[row][col] for row in range(self.data['shape'][0])) == self.data['shape'][0] / 3
            )
            self.addConstraint(
                mip.xsum(self.IVars[row][col] for row in range(self.data['shape'][0])) == self.data['shape'][0] / 3
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixCells = [(cell['row'], cell['col']) for cell in self.data['fixed']]
        board = [[None] * self.data['shape'][1] for _ in range(self.data['shape'][0])]
        for row, col in itertools.product(
            range(self.data['shape'][0]),
            range(self.data['shape'][1])
        ):
            if self.XVars[row][col].x == 1:
                board[row][col] = 'X'
            elif self.OVars[row][col].x == 1:
                board[row][col] = 'O'
            elif self.IVars[row][col].x == 1:
                board[row][col] = 'I'
            else:
                raise ValueError(f'Cell ({row, col}) not containt any symbol')
        for row in range(self.data['shape'][0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data['shape'][1]):
                if (row, col) in fixCells:
                    if board[row][col] == 'X':
                        renderRow += f' {Colors.BOLD}{Colors.GRAY}X{Colors.ENDC} '
                    elif board[row][col] == 'O':
                        renderRow += f' {Colors.BOLD}{Colors.GRAY}O{Colors.ENDC} '
                    else:
                        renderRow += f' {Colors.BOLD}{Colors.GRAY}I{Colors.ENDC} '
                else:
                    if board[row][col] == 'X':
                        renderRow += f' {Colors.BOLD}{Colors.RED}X{Colors.ENDC} '
                    elif board[row][col] == 'O':
                        renderRow += f' {Colors.BOLD}{Colors.BLUE}O{Colors.ENDC} '
                    else:
                        renderRow += f' {Colors.BOLD}{Colors.GREEN}I{Colors.ENDC} '
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
