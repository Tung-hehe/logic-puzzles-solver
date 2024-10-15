import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Troix(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verify_data(self) -> None:
        if self.data.shape[0] % 3 != 0 or self.data.shape[1] % 3 != 0:
            raise ValueError(f"Shape mod 3 must be equal 0, not {self.data.shape}")
        for cell in self.data.fixed:
            if (
                cell['row'] < 0 or cell['row'] >= self.data.shape[0]
                or cell['col'] < 0 or cell['col'] >= self.data.shape[1]
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data.shape}.")
            if cell['val'] not in ['X', 'O', 'I']:
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
        self.o_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'o_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0])
        ]
        self.i_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'i_{row}_{col}')
                for col in range(self.data.shape[1])
            ]
            for row in range(self.data.shape[0])
        ]
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_each_cell_contains_one_symbol()
        self.add_fixed_cell_constraints()
        self.add_limit_consecutive_symbol_each_row_constraints()
        self.add_limit_consecutive_symbol_each_col_constraints()
        self.add_equal_symbols_each_row_constraints()
        self.add_equal_symbols_each_col_constraints()
        return None

    def add_each_cell_contains_one_symbol(self) -> None:
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[0])):
            self.add_constraint(
                self.x_vars[row][col] + self.o_vars[row][col] + self.i_vars[row][col] == 1
            )

    def add_fixed_cell_constraints(self) -> None:
        for cell in self.data.fixed:
            if cell['val'] == 'X':
                self.add_constraint(self.x_vars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'O':
                self.add_constraint(self.o_vars[cell['row']][cell['col']] == 1)
            elif cell['val'] == 'I':
                self.add_constraint(self.i_vars[cell['row']][cell['col']] == 1)
            else:
                raise ValueError(f"In valid value in cell {cell}")

    def add_limit_consecutive_symbol_each_row_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1] - self.data.symbol_number):
                self.add_constraint(
                    mip.xsum(
                        self.x_vars[row][col + gap] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
                self.add_constraint(
                    mip.xsum(
                        self.o_vars[row][col + gap] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
                self.add_constraint(
                    mip.xsum(
                        self.i_vars[row][col + gap] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
        return None

    def add_limit_consecutive_symbol_each_col_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            for row in range(self.data.shape[0] - self.data.symbol_number):
                self.add_constraint(
                    mip.xsum(
                        self.x_vars[row + gap][col] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
                self.add_constraint(
                    mip.xsum(
                        self.o_vars[row + gap][col] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
                self.add_constraint(
                    mip.xsum(
                        self.i_vars[row + gap][col] for gap in range(self.data.symbol_number + 1)
                    ) <= self.data.symbol_number
                )
        return None

    def add_equal_symbols_each_row_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            self.add_constraint(
                mip.xsum(
                    self.x_vars[row][col] for col in range(self.data.shape[1])
                ) == self.data.shape[1] / 3
            )
            self.add_constraint(
                mip.xsum(
                    self.o_vars[row][col] for col in range(self.data.shape[1])
                ) == self.data.shape[1] / 3
            )
            self.add_constraint(
                mip.xsum(
                    self.i_vars[row][col] for col in range(self.data.shape[1])
                ) == self.data.shape[1] / 3
            )
        return None

    def add_equal_symbols_each_col_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col] for row in range(self.data.shape[0])) == self.data.shape[0] / 3
            )
            self.add_constraint(
                mip.xsum(self.o_vars[row][col] for row in range(self.data.shape[0])) == self.data.shape[0] / 3
            )
            self.add_constraint(
                mip.xsum(self.i_vars[row][col] for row in range(self.data.shape[0])) == self.data.shape[0] / 3
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixed_cells = [(cell['row'], cell['col']) for cell in self.data.fixed]
        board = [[None] * self.data.shape[1] for _ in range(self.data.shape[0])]
        for row, col in itertools.product(
            range(self.data.shape[0]),
            range(self.data.shape[1])
        ):
            if self.x_vars[row][col].x == 1:
                board[row][col] = 'X'
            elif self.o_vars[row][col].x == 1:
                board[row][col] = 'O'
            elif self.i_vars[row][col].x == 1:
                board[row][col] = 'I'
            else:
                raise ValueError(f'Cell ({row, col}) not contain any symbol')
        for row in range(self.data.shape[0]):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if (row, col) in fixed_cells:
                    if board[row][col] == 'X':
                        render_row += f' {Colors.BOLD}{Colors.GRAY}X{Colors.ENDC} '
                    elif board[row][col] == 'O':
                        render_row += f' {Colors.BOLD}{Colors.GRAY}O{Colors.ENDC} '
                    else:
                        render_row += f' {Colors.BOLD}{Colors.GRAY}I{Colors.ENDC} '
                else:
                    if board[row][col] == 'X':
                        render_row += f' {Colors.BOLD}{Colors.RED}X{Colors.ENDC} '
                    elif board[row][col] == 'O':
                        render_row += f' {Colors.BOLD}{Colors.BLUE}O{Colors.ENDC} '
                    else:
                        render_row += f' {Colors.BOLD}{Colors.GREEN}I{Colors.ENDC} '
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
