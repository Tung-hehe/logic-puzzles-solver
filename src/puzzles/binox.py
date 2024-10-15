import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Binox(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verify_data(self) -> None:
        if self.data.shape[0] % 2 == 1 or self.data.shape[1] % 2 == 1:
            raise ValueError(f"Shape must be even, not {self.data.shape}")
        for cell in self.data.fixed:
            if (
                cell['row'] < 0 or cell['row'] >= self.data.shape[0]
                or cell['col'] < 0 or cell['col'] >= self.data.shape[1]
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data.shape}.")
            if cell['val'] not in ['X', 'O']:
                raise ValueError(f"Fixed value in cell {cell} should be 'X' or 'O'.")
        return None

    def add_variables(self) -> None:
        super().add_variables()
        self.x_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'x_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0])
        ]
        self.y_vars = {}
        for col in range(self.data.shape[1]):
            for row1, row2 in itertools.combinations(range(self.data.shape[0]), 2):
                self.y_vars[(row1, row2, col)] = self.add_variable(
                    vtype=mip.BINARY, name=f'y_{row1}_{row2}_{col}'
                )
        self.z_vars = {}
        for row in range(self.data.shape[0]):
            for col1, col2 in itertools.combinations(range(self.data.shape[1]), 2):
                self.z_vars[(col1, col2, row)] = self.add_variable(
                    vtype=mip.BINARY, name=f'y_{row1}_{col2}_{row}'
                )
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_fixed_cell_constraints()
        self.add_limit_consecutive_symbol_each_row_constraints()
        self.add_limit_consecutive_symbol_each_col_constraints()
        self.add_equal_symbols_each_row_constraints()
        self.add_equal_symbols_each_col_constraints()
        self.add_unique_row_constraints()
        self.add_unique_col_constraints()
        return None

    def add_limit_consecutive_symbol_each_row_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1] - self.data.symbol_number):
                self.add_constraint(mip.xsum(
                    self.x_vars[row][col + gap] for gap in range(self.data.symbol_number + 1)
                ) <= self.data.symbol_number)
                self.add_constraint(
                    mip.xsum(self.x_vars[row][col + gap] for gap in range(self.data.symbol_number + 1)) >= 1
                )
        return None

    def add_limit_consecutive_symbol_each_col_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            for row in range(self.data.shape[0] - self.data.symbol_number):
                self.add_constraint(mip.xsum(
                    self.x_vars[row + gap][col] for gap in range(self.data.symbol_number + 1)
                ) <= self.data.symbol_number)
                self.add_constraint(
                    mip.xsum(self.x_vars[row + gap][col] for gap in range(self.data.symbol_number + 1)) >= 1
                )
        return None

    def add_equal_symbols_each_row_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col] for col in range(self.data.shape[1])) == self.data.shape[1] / 2
            )
        return None

    def add_equal_symbols_each_col_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col] for row in range(self.data.shape[0])) == self.data.shape[0] / 2
            )
        return None

    def add_fixed_cell_constraints(self) -> None:
        for cell in self.data.fixed:
            if cell['val'] == 'X':
                self.add_constraint(self.x_vars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'O':
                self.add_constraint(self.x_vars[cell['row']][cell['col']] == 0)
            else:
                raise ValueError(f"In valid value in cell {cell}")

    def add_unique_row_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            for row1, row2 in itertools.combinations(range(self.data.shape[0]), 2):
                self.add_constraint(
                    self.y_vars[(row1, row2, col)] + self.x_vars[row1][col] + self.x_vars[row2][col] >= 1
                )
                self.add_constraint(
                    self.y_vars[(row1, row2, col)] + self.x_vars[row1][col] <= 1 + self.x_vars[row2][col]
                )
                self.add_constraint(
                    self.y_vars[(row1, row2, col)]  + self.x_vars[row2][col] <= 1 + self.x_vars[row1][col]
                )
                self.add_constraint(
                    self.x_vars[row1][col] + self.x_vars[row2][col] <= 1 + self.y_vars[(row1, row2, col)]
                )
        for row1, row2 in itertools.combinations(range(self.data.shape[0]), 2):
            self.add_constraint(
                mip.xsum(self.y_vars[(row1, row2, col)] for col in range(self.data.shape[1])) <= self.data.shape[1] - 1
            )
        return None

    def add_unique_col_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            for col1, col2 in itertools.combinations(range(self.data.shape[1]), 2):
                self.add_constraint(
                    self.z_vars[(col1, col2, row)] + self.x_vars[row][col1] + self.x_vars[row][col2] >= 1
                )
                self.add_constraint(
                    self.z_vars[(col1, col2, row)] + self.x_vars[row][col1] <= 1 + self.x_vars[row][col2]
                )
                self.add_constraint(
                    self.z_vars[(col1, col2, row)]  + self.x_vars[row][col2] <= 1 + self.x_vars[row][col1]
                )
                self.add_constraint(
                    self.x_vars[row][col1] + self.x_vars[row][col2] <= 1 + self.z_vars[(col1, col2, row)]
                )
        for col1, col2 in itertools.combinations(range(self.data.shape[1]), 2):
            self.add_constraint(
                mip.xsum(self.z_vars[(col1, col2, row)] for row in range(self.data.shape[0])) <= self.data.shape[0] - 1
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixed_cells = [(cell['row'], cell['col']) for cell in self.data.fixed]
        for row in range(self.data.shape[0]):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if (row, col) in fixed_cells:
                    if self.x_vars[row][col].x == 1:
                        render_row += f' {Colors.BOLD}{Colors.GRAY}X{Colors.ENDC} '
                    else:
                        render_row += f' {Colors.BOLD}{Colors.GRAY}O{Colors.ENDC} '
                else:
                    if self.x_vars[row][col].x == 1:
                        render_row += f' {Colors.BOLD}{Colors.RED}X{Colors.ENDC} '
                    else:
                        render_row += f' {Colors.BOLD}{Colors.BLUE}O{Colors.ENDC} '
                if col == self.data.shape[1] - 1:
                    render_row += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    render_row += f'{Colors.GRAY}|{Colors.ENDC}'
                    node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0:
                    render_up_row += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    render_up_row += f'{Colors.GRAY}---{Colors.ENDC}{node}'
            print(render_up_row)
            print(render_row)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}')
        return None
