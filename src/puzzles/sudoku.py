import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Sudoku(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.modifiy_fixed_cells_values()
        return None

    def verify_data(self) -> None:
        self.block_shape = int(self.data.shape ** 0.5)
        if self.block_shape ** 2 != self.data.shape:
            raise ValueError(f"Invalid shape")
        for cell in self.data.fixed_cells:
            if (
                cell['row'] < 0 or cell['row'] >= self.data.shape
                or cell['col'] < 0 or cell['col'] >= self.data.shape
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data.shape}.")
            if cell['val'] > self.data.shape:
                raise ValueError(f"Fixed value in cell {cell} should be in range [1, {self.data.shape}].")
        return None

    def modifiy_fixed_cells_values(self):
        for i in range(len(self.data.fixed_cells)):
            self.data.fixed_cells[i]['val'] = self.data.fixed_cells[i]['val'] - 1
        return None

    def add_variables(self) -> None:
        super().add_variables()
        self.x_vars = [
            [
                [
                    self.add_variable(vtype=mip.BINARY, name=f'x_{row}_{col}_{val}')
                    for val in range(self.data.shape)
                ]
                for col in range(self.data.shape)
            ]
            for row in range(self.data.shape)
        ]
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_fixed_cell_constraints()
        self.add_each_cell_contains_one_value_contraints()
        self.add_unique_number_each_row_constraints()
        self.add_unique_number_each_column_constraints()
        self.add_unique_number_each_block_constraints()
        return None

    def add_each_cell_contains_one_value_contraints(self) -> None:
        for row, col in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col][val] for val in range(self.data.shape)) == 1
            )
        return None

    def add_fixed_cell_constraints(self) -> None:
        for cell in self.data.fixed_cells:
            self.add_constraint(self.x_vars[cell['row']][cell['col']][cell['val']] == 1)
        return None

    def add_unique_number_each_row_constraints(self) -> None:
        for row, val in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col][val] for col in range(self.data.shape)) == 1
            )
        return None

    def add_unique_number_each_column_constraints(self) -> None:
        for col, val in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col][val] for row in range(self.data.shape)) == 1
            )
        return None

    def add_unique_number_each_block_constraints(self) -> None:
        for row, col in itertools.product(
            range(0, self.data.shape, self.block_shape), range(0, self.data.shape, self.block_shape)
        ):
            for val in range(self.data.shape):
                self.add_constraint(
                    mip.xsum(
                        self.x_vars[row + step_row][col + step_col][val]
                        for step_row, step_col in itertools.product(
                            range(self.block_shape), range(self.block_shape)
                        )
                    ) == 1
                )
        return None

    def visualize(self) -> None:
        super().visualize()
        fixed_cells = {(cell['row'], cell['col']): cell['val'] for cell in self.data.fixed_cells}
        for row in range(self.data.shape):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape):
                if (row, col) in fixed_cells.keys():
                    render_row += f' {Colors.BOLD}{Colors.GRAY}{fixed_cells[(row, col)]}{Colors.ENDC} '
                else:
                    value = int(sum(val * self.x_vars[row][col][val].x for val in range(self.data.shape)))
                    render_row += f' {Colors.BOLD}{Colors.BLUE}{value + 1}{Colors.ENDC} '
                if (col + 1) % self.block_shape == 0:
                    render_row += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    render_row += f'{Colors.GRAY}|{Colors.ENDC}'
                    node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row % self.block_shape == 0:
                    render_up_row += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    render_up_row += f'{Colors.GRAY}---{Colors.ENDC}{node}'
            print(render_up_row)
            print(render_row)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape + 1))}{Colors.ENDC}')
        return None
