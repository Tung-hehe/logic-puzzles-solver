import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors


class StarBattle(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verify_data(self) -> None:
        sorted_data = sorted(sum(
            [
                [(cell['row'], cell['col']) for cell in cage]
                for cage in self.data.cages
            ], start=[]
        ))
        for index, (row, col) in enumerate(itertools.product(
            range(self.data.shape[0]), range(self.data.shape[1])
        )):
            if (row, col) != sorted_data[index]:
                cell = {"row": row, "col": col}
                raise ValueError(f"Cell {cell} has a problem!")
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
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_star_number_each_row_constraints()
        self.add_star_number_each_column_constraints()
        self.add_star_number_each_cage_constraints()
        self.add_stars_not_adjacent_each_other_constraints()
        return None

    def add_star_number_each_row_constraints(self) -> None:
        for row in range(self.data.shape[0]):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col] for col in range(self.data.shape[1])) == self.data.star_number
            )
        return None

    def add_star_number_each_column_constraints(self) -> None:
        for col in range(self.data.shape[1]):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col] for row in range(self.data.shape[0])) == self.data.star_number
            )
        return None

    def add_star_number_each_cage_constraints(self) -> None:
        for cage in self.data.cages:
            self.add_constraint(
                mip.xsum(self.x_vars[cell['row']][cell['col']] for cell in cage) == self.data.star_number
            )
        return None

    def add_stars_not_adjacent_each_other_constraints(self) -> None:
        # The stars may not be adjacent to each other (not even diagonally).
        blocks = {}
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[1])):
            blocks[(row, col)] = []
            for gap_row, gap_col in itertools.product([-1, 0, 1], [-1, 0, 1]):
                if gap_row == 0 and gap_col == 0:
                    continue
                if 0 <= row + gap_row < self.data.shape[0] and 0 <= col + gap_col < self.data.shape[1]:
                    blocks[(row, col)].append((row + gap_row, col + gap_col))
        for cell, neighbors in blocks.items():
            neighbor_cells_number = len(neighbors)
            self.add_constraint(
                neighbor_cells_number * self.x_vars[cell[0]][cell[1]]
                + mip.xsum(self.x_vars[row][col] for row, col in neighbors)
                <= neighbor_cells_number
            )
        return None

    def visualize(self) -> None:
        super().visualize()
        cages = [[None] * self.data.shape[1] for _ in range(self.data.shape[0])]
        for index, cage in enumerate(self.data.cages):
            for cell in cage:
                if cages[cell['row']][cell['col']] is not None:
                    raise ValueError(f'Cell {cell} is duplicated')
                cages[cell['row']][cell['col']] = index
        for row in range(self.data.shape[0]):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if self.x_vars[row][col].x == 1:
                    render_row += f' {Colors.BOLD}{Colors.GREEN}⚝{Colors.ENDC} '
                else:
                    render_row += f'   '
                if col == self.data.shape[1] - 1 or cages[row][col] != cages[row][col + 1]:
                    render_row += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    cross_node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    render_row += f' '
                    cross_node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0 or cages[row][col] != cages[row - 1][col]:
                    normal_cross_node = f'{Colors.GRAY}+{Colors.ENDC}'
                    if render_up_row.endswith(normal_cross_node):
                        render_up_row = render_up_row[:len(render_up_row) - len(normal_cross_node)]
                        render_up_row += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        render_up_row += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    render_up_row += f'   {cross_node}'
            print(render_up_row)
            print(render_row)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}')
        return None
