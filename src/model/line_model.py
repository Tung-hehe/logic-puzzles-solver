import itertools

from pathlib import Path

import mip

from .base_model import BaseModel


class LineModel(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def add_variables(self) -> None:
        super().add_variables()
        # Horizontal line variables
        self.h_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'h_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0] + 1)
        ]
        # Vertical line variables
        self.v_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1] + 1)
            ]
            for row in range(self.data.shape[0])
        ]
        # Point variables
        self.p_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'p_{row}_{col}')
                for col in range(self.data.shape[1] + 1)
            ]
            for row in range(self.data.shape[0] + 1)
        ]
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_lines_connected_into_disjoint_closed_cycles_constraint()
        return None

    def add_lines_connected_into_disjoint_closed_cycles_constraint(self) -> None:
        for row, col in itertools.product(
            range(self.data.shape[0] + 1), range(self.data.shape[1] + 1)
        ):
            lines_vars = []
            if row > 0:
                lines_vars.append(self.v_vars[row - 1][col])
            if row < self.data.shape[0]:
                lines_vars.append(self.v_vars[row][col])
            if col > 0:
                lines_vars.append(self.h_vars[row][col - 1])
            if col < self.data.shape[1]:
                lines_vars.append(self.h_vars[row][col])
            if len(lines_vars) > 0:
                self.add_constraint(
                    mip.xsum(lines_vars) == 2*self.p_vars[row][col]
                )
        return None

    def find_next_line(self, line) -> tuple:
        if line[0] == 'h':
            pass
        elif line[0] == 'v':
            pass
        else:
            raise ValueError(f'Invalid direction {line[0]}')

    def find_cycles(self) -> list[list]:
        all_lines = [
            (row, col, 'h') for row, col in itertools.product(
                range(self.data.shape[0] + 1), range(self.data.shape[1])
            ) if self.h_vars[row][col].x == 1
        ] + [
            (row, col, 'v') for row, col in itertools.product(
                range(self.data.shape[0]), range(self.data.shape[1] + 1)
            ) if self.v_vars[row][col].x == 1
        ]
        cycles = []
        while True:
            if len(all_lines) == 0:
                break
            cycle = [all_lines.pop(0)]
            while True:
                for index, line in enumerate(all_lines):
                    h_h_connection = (
                        cycle[-1][-1] == 'h' == line[-1]
                        and cycle[-1][0] == line[0]
                        and cycle[-1][1] - line[1] in [-1, 1]
                    )
                    h_v_connection = (
                        cycle[-1][-1] == 'h' != line[-1]
                        and 0 <= cycle[-1][0] - line[0] <= 1
                        and 0 <= line[1] - cycle[-1][1] <= 1
                    )
                    v_v_connection = (
                        cycle[-1][-1] == 'v' == line[-1]
                        and cycle[-1][0] - line[0] in [-1, 1]
                        and cycle[-1][1] == line[1]
                    )
                    v_h_connection = (
                        cycle[-1][-1] == 'v' != line[-1]
                        and 0 <= line[0] - cycle[-1][0] <= 1
                        and 0 <= cycle[-1][1] - line[1] <= 1
                    )
                    if (
                        h_h_connection
                        or h_v_connection
                        or v_v_connection
                        or v_h_connection
                    ):
                        cycle.append(all_lines.pop(index))
                        break
                else:
                    cycles.append(cycle)
                    break
        return cycles

    def solve(self) -> None:
        self._model.optimize()
        while True:
            cycles = self.find_cycles()
            if len(cycles) == 1:
                self.calculate_solving_time()
                break
            if self._model.status != mip.OptimizationStatus.OPTIMAL:
                self.raise_error_infeasible()
            for cycle in cycles:
                var_lines = [
                    self.h_vars[line[0]][line[1]]
                    if line[-1] == 'h' else self.v_vars[line[0]][line[1]]
                    for line in cycle
                ]
                self.add_constraint(mip.xsum(var_lines) <= len(var_lines) - 1)
            self._model.optimize()
        return None
