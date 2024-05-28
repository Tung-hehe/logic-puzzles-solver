import itertools

from pathlib import Path

import mip

from .model import Model

from src.utils import PuzzleName, Colors


class StarBattle(Model):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath, PuzzleName.StarBattle)
        self.verifyData()
        return None

    def verifyData(self) -> None:
        sortedData = sorted(sum(
            [
                [(cell['row'], cell['col']) for cell in cage]
                for cage in self.data['cages']
            ], start=[]
        ))
        assert sortedData == [
            (row, col) for row, col in itertools.product(
                range(self.data['shape']), range(self.data['shape'])
            )
        ]
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.xVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'x_{row}_{col}')
                for row in range(self.data['shape'])
            ]
            for col in range(self.data['shape'])
        ]
        return None

    def addContraints(self) -> None:
        super().addContraints()
        self.addTwoStarsEachRowConstraints()
        self.addTwoStarsEachColumnConstraints()
        self.addTwoStarsEachCageConstraints()
        self.addStarsNotBeAdjacentEachOtherConstraints()
        return None

    def addTwoStarsEachRowConstraints(self) -> None:
        for row in range(self.data['shape']):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for col in range(self.data['shape'])) == self.data['nStars']
            )
        return None

    def addTwoStarsEachColumnConstraints(self) -> None:
        for col in range(self.data['shape']):
            self.addConstraint(
                mip.xsum(self.xVars[row][col] for row in range(self.data['shape'])) == self.data['nStars']
            )
        return None

    def addTwoStarsEachCageConstraints(self) -> None:
        for cage in self.data['cages']:
            self.addConstraint(
                mip.xsum(self.xVars[cell['row']][cell['col']] for cell in cage) == self.data['nStars']
            )
        return None

    def addStarsNotBeAdjacentEachOtherConstraints(self) -> None:
        # The stars may not be adjacent to each other (not even diagonally).
        blocks = {}
        for row, col in itertools.product(range(self.data['shape']), range(self.data['shape'])):
            blocks[(row, col)] = []
            for gapRow, gapCol in itertools.product([-1, 0, 1], [-1, 0, 1]):
                if gapRow == 0 and gapCol == 0:
                    continue
                if 0 <= row + gapRow < self.data['shape'] and 0 <= col + gapCol < self.data['shape']:
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
        cages = [[None] * self.data['shape'] for _ in range(self.data['shape'])]
        for index, cage in enumerate(self.data['cages']):
            for cell in cage:
                assert cages[cell['row']][cell['col']] is None
                cages[cell['row']][cell['col']] = index
        for row in range(self.data['shape']):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data['shape']):
                if self.xVars[row][col].x == 1:
                    renderRow += f' {Colors.BOLD}{Colors.GREEN}⚝{Colors.ENDC} '
                else:
                    renderRow += f'   '
                if col == self.data['shape'] - 1 or cages[row][col] != cages[row][col + 1]:
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
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data["shape"] + 1))}{Colors.ENDC}')
        return None
