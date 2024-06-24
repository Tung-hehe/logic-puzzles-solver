import itertools

from pathlib import Path

import mip

from .baseModel import BaseModel


class LineModel(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def addVariables(self) -> None:
        super().addVariables()
        # Horizontal line variables
        self.hVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'h_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0] + 1)
        ]
        # Vertical line variables
        self.vVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1] + 1)
            ]
            for row in range(self.data.shape[0])
        ]
        # Point variables
        self.pVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'p_{row}_{col}')
                for col in range(self.data.shape[1] + 1)
            ]
            for row in range(self.data.shape[0] + 1)
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addLinesConnectedIntoDisjointClosedCyclesConstraint()
        return None

    def addLinesConnectedIntoDisjointClosedCyclesConstraint(self) -> None:
        for row, col in itertools.product(
            range(self.data.shape[0] + 1), range(self.data.shape[1] + 1)
        ):
            linesVars = []
            if row > 0:
                linesVars.append(self.vVars[row - 1][col])
            if row < self.data.shape[0]:
                linesVars.append(self.vVars[row][col])
            if col > 0:
                linesVars.append(self.hVars[row][col - 1])
            if col < self.data.shape[1]:
                linesVars.append(self.hVars[row][col])
            if len(linesVars) > 0:
                self.addConstraint(
                    mip.xsum(linesVars) == 2*self.pVars[row][col]
                )
        return None

    def findNextLine(self, line) -> tuple:
        if line[0] == 'h':
            pass
        elif line[0] == 'v':
            pass
        else:
            raise ValueError(f'Invalid direction {line[0]}')

    def findCycles(self) -> list[list]:
        allLines = [
            (row, col, 'h') for row, col in itertools.product(
                range(self.data.shape[0] + 1), range(self.data.shape[1])
            ) if self.hVars[row][col].x == 1
        ] + [
            (row, col, 'v') for row, col in itertools.product(
                range(self.data.shape[0]), range(self.data.shape[1] + 1)
            ) if self.vVars[row][col].x == 1
        ]
        cycles = []
        while True:
            if len(allLines) == 0:
                break
            cycle = [allLines.pop(0)]
            while True:
                for index, line in enumerate(allLines):
                    hLineConnectWithHLine = (
                        cycle[-1][-1] == 'h' == line[-1]
                        and cycle[-1][0] == line[0]
                        and cycle[-1][1] - line[1] in [-1, 1]
                    )
                    hLineConnectWithVLine = (
                        cycle[-1][-1] == 'h' != line[-1]
                        and 0 <= cycle[-1][0] - line[0] <= 1
                        and 0 <= line[1] - cycle[-1][1] <= 1
                    )
                    vLineConnectWithVLine = (
                        cycle[-1][-1] == 'v' == line[-1]
                        and cycle[-1][0] - line[0] in [-1, 1]
                        and cycle[-1][1] == line[1]
                    )
                    vLineConnectWithHLine = (
                        cycle[-1][-1] == 'v' != line[-1]
                        and 0 <= line[0] - cycle[-1][0] <= 1
                        and 0 <= cycle[-1][1] - line[1] <= 1
                    )
                    if (
                        hLineConnectWithHLine
                        or hLineConnectWithVLine
                        or vLineConnectWithVLine
                        or vLineConnectWithHLine
                    ):
                        cycle.append(allLines.pop(index))
                        break
                else:
                    cycles.append(cycle)
                    break
        return cycles

    def solve(self) -> None:
        self._model.optimize()
        while True:
            cycles = self.findCycles()
            if len(cycles) == 1:
                self.calculateSolvingTime()
                break
            if self._model.status != mip.OptimizationStatus.OPTIMAL:
                self.raiseErrorInfeasible()
            for cycle in cycles:
                varLines = [
                    self.hVars[line[0]][line[1]]
                    if line[-1] == 'h' else self.vVars[line[0]][line[1]]
                    for line in cycle
                ]
                self.addConstraint(mip.xsum(varLines) <= len(varLines) - 1)
            self._model.optimize()
        return None
