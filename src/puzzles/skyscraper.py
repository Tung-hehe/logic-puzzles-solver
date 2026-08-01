import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class Skyscraper(BaseModel):

    def __init__(self, dataPath: str) -> None:
        super().__init__(Path(dataPath))
        self.modifiy_fixed_cells_values()
        return None

    def verify_data(self) -> None:
        for direction in ['top', 'bottom', 'left', 'right']:
            if direction not in self.data.visible.keys():
                raise ValueError(f"Missing visible clues for direction '{direction}'.")
            if len(self.data.visible[direction]) != self.data.shape:
                raise ValueError(f"Visible clues '{direction}' must have {self.data.shape} values.")
        for cell in self.data.fixed_cells:
            if (
                cell['row'] < 0 or cell['row'] >= self.data.shape
                or cell['col'] < 0 or cell['col'] >= self.data.shape
            ):
                raise ValueError(f"Cell {cell} out of puzzle with shape {self.data.shape}.")
            if cell['val'] < 1 or cell['val'] > self.data.shape:
                raise ValueError(f"Fixed value in cell {cell} should be in range [1, {self.data.shape}].")
        return None

    def modifiy_fixed_cells_values(self) -> None:
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
        self.add_each_cell_contains_one_value_constraints()
        self.add_unique_number_each_row_constraints()
        self.add_unique_number_each_column_constraints()
        self.add_visible_building_constraints()
        return None

    def add_fixed_cell_constraints(self) -> None:
        for cell in self.data.fixed_cells:
            self.add_constraint(self.x_vars[cell['row']][cell['col']][cell['val']] == 1)
        return None

    def add_each_cell_contains_one_value_constraints(self) -> None:
        for row, col in itertools.product(range(self.data.shape), range(self.data.shape)):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col][val] for val in range(self.data.shape)) == 1
            )
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

    def get_sight_lines(self) -> dict:
        shape = self.data.shape
        rows = [[(row, col) for col in range(shape)] for row in range(shape)]
        cols = [[(row, col) for row in range(shape)] for col in range(shape)]
        return {
            'left': [(line, self.data.visible['left'][row]) for row, line in enumerate(rows)],
            'right': [(line[::-1], self.data.visible['right'][row]) for row, line in enumerate(rows)],
            'top': [(line, self.data.visible['top'][col]) for col, line in enumerate(cols)],
            'bottom': [(line[::-1], self.data.visible['bottom'][col]) for col, line in enumerate(cols)],
        }

    def add_visible_building_constraints(self) -> None:
        for direction, sight_lines in self.get_sight_lines().items():
            for index, (line, visible_number) in enumerate(sight_lines):
                self.add_visible_building_line_constraints(f'{direction}_{index}', line, visible_number)
        return None

    def add_visible_building_line_constraints(self, tag: str, line: list, visible_number: int) -> None:
        # See ./docs/skyscraper.md for the derivation of this "record-from-the-front" encoding.
        shape = self.data.shape
        visible_vars = []
        for position in range(shape):
            row, col = line[position]
            for val in range(shape):
                z = self.add_variable(vtype=mip.BINARY, name=f'visible_{tag}_{position}_{val}')
                visible_vars.append(z)
                taller_before = mip.xsum(
                    self.x_vars[before_row][before_col][before_val]
                    for before_row, before_col in line[:position]
                    for before_val in range(val + 1, shape)
                )
                self.add_constraint(taller_before + position * z - position <= 0)
                self.add_constraint(self.x_vars[row][col][val] - z >= 0)
                self.add_constraint(self.x_vars[row][col][val] - taller_before - z <= 0)
        self.add_constraint(mip.xsum(visible_vars) == visible_number)
        return None

    def visualize(self) -> None:
        super().visualize()
        shape = self.data.shape
        fixed_cells = {(cell['row'], cell['col']): cell['val'] for cell in self.data.fixed_cells}
        top_line = f'{Colors.GRAY}    '
        for val in self.data.visible['top']:
            top_line += str(val).center(4)
        top_line += f'{Colors.ENDC}'
        print(top_line)
        for row in range(shape):
            render_up_row = f'   {Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = (
                f'{Colors.GRAY}{str(self.data.visible["left"][row]).center(3)}{Colors.ENDC}'
                f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            )
            for col in range(shape):
                if (row, col) in fixed_cells.keys():
                    render_row += f' {Colors.BOLD}{Colors.GRAY}{fixed_cells[(row, col)] + 1}{Colors.ENDC} '
                else:
                    render_row += f' {Colors.BOLD}{Colors.BLUE}{self.solution[row][col]}{Colors.ENDC} '
                render_row += f'{Colors.GRAY}|{Colors.ENDC}' if col < shape - 1 else f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                render_up_row += f'{Colors.GRAY}---+{Colors.ENDC}'
            render_row += f'{Colors.GRAY}{str(self.data.visible["right"][row]).center(3)}{Colors.ENDC}'
            print(render_up_row)
            print(render_row)
        print(f'   {Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (shape + 1))}{Colors.ENDC}')
        bottom_line = f'{Colors.GRAY}    '
        for val in self.data.visible['bottom']:
            bottom_line += str(val).center(4)
        bottom_line += f'{Colors.ENDC}'
        print(bottom_line)
        return None

    def to_solution(self) -> None:
        self.solution = [[None] * self.data.shape for _ in range(self.data.shape)]
        for row, col in itertools.product(range(self.data.shape), range(self.data.shape)):
            value = int(sum(val * self.x_vars[row][col][val].x for val in range(self.data.shape))) + 1
            self.solution[row][col] = value
        return None
