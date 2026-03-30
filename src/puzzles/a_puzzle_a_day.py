import calendar
import itertools

from datetime import datetime

import mip

from src.model import BaseModel
from src.utils import Colors


PIECES = {
    'O': {(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)},
    'P': {(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)},
    'L': {(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)},
    'C': {(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)},
    'V': {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)},
    'S': {(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)},
    'J': {(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)},
    'F': {(0, 0), (1, 0), (1, 1), (2, 0), (3, 0)}
}

PIECES_COLOR = {
    "O": '\033[48;5;196m',
    "P": '\033[48;5;202m',
    "L": '\033[48;5;220m',
    "C": '\033[48;5;82m',
    "V": '\033[48;5;27m',
    "S": '\033[48;5;93m',
    "J": '\033[48;5;201m',
    "F": '\033[48;5;244m',
}

class APuzzleADay(BaseModel):

    """
    Piece name:
        O:   ___
            |   |
            |   |
            |___|

        P:   _
            | |_
            |   |
            |___|

        L:   _
            | |
            | |
            | |_
            |___|

        C:   ____
            |  __|
            | |__
            |____|

        V:   _
            | |
            | |___
            |_____|

        S:   ___
            |_  |
              | |_
              |___|

        J:   _
            | |_
            |_  |
              | |
              |_|

        F:   _
            | |_
            |  _|
            | |
            |_|
    """

    def __init__(self, date: str) -> None:
        self.start_time = datetime.now()
        date = date.split('-')
        self.day = int(date[0])
        self.day_cell = (2 + (self.day - 1) // 7, (self.day - 1) % 7)
        self.month = int(date[1])
        self.month_cell = ((self.month - 1) // 6, (self.month - 1) % 6)
        self.month = calendar.month_abbr[self.month]

        self.size = 7
        self.block_cells = []

        self._model = mip.Model(solver_name='CBC')
        self._model.solver.set_emphasis(mip.SearchEmphasis.FEASIBILITY)
        self._model.verbose = 0
        self.invalid_cells = [(0, 6), (1, 6), (6, 3), (6, 4), (6, 5), (6, 6)]
        self.valid_cells = {
            (r, c)
            for r, c in itertools.product(range(self.size), range(self.size))
            if (r, c) not in self.invalid_cells
        }

        self.get_all_pieces_configs()
        self.get_cell_configs()
        return None

    def add_variables(self) -> None:
        self.x_vars = {
            piece: {
                config: self._model.add_var(var_type=mip.BINARY, name=f'v_{piece}_{config}')
                for config in self.configs[piece].keys()
            }
            for piece in self.configs.keys()
        }
        return None

    def add_constraints(self) -> None:
        self.add_each_cell_belong_to_one_piece_except_day_cell_and_month_cell_constraints()
        self.add_piece_only_use_one_config_constraints()
        return None

    def add_each_cell_belong_to_one_piece_except_day_cell_and_month_cell_constraints(self) -> None:
        for cell, configs in self.cells_configs.items():
            lhs = mip.xsum(self.x_vars[config[0]][config[1]] for config in configs)
            if cell not in [self.day_cell, self.month_cell]:
                rhs = 1
            else:
                rhs = 0
            self.add_constraint(lhs == rhs)
        return None

    def add_piece_only_use_one_config_constraints(self) -> None:
        for piece, configs in self.configs.items():
            self.add_constraint(mip.xsum(self.x_vars[piece][config] for config in configs.keys()) == 1)
        return None
    def get_cell_configs(self):
        self.cells_configs = {}
        for piece, configs in self.configs.items():
            for idx, config in configs.items():
                for cell in config:
                    if cell not in self.cells_configs:
                        self.cells_configs[cell] = []
                    self.cells_configs[cell].append((piece, idx))
        return None

    def normalize_piece(self, shape: set[tuple[int, int]]) -> set[tuple[int, int]]:
        min_r = min(r for r, _ in shape)
        min_c = min(c for _, c in shape)
        return {(r - min_r, c - min_c) for r, c in shape}

    def rotate_piece(self, shape) -> set[tuple[int, int]]:
        return {(-c, r) for r, c in shape}

    def flip_piece(self, shape) -> set[tuple[int, int]]:
        return {(r, -c) for r, c in shape}

    def get_all_pieces_orientations(self, shape: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
        shapes = set()
        s = shape
        for _ in range(4):
            s = self.rotate_piece(s)
            shapes.add(frozenset(self.normalize_piece(s)))
            shapes.add(frozenset(self.normalize_piece(self.flip_piece(s))))
        return [set(s) for s in shapes]

    def generate_piece_configs(self, shape: set[tuple[int, int]]) -> list[tuple[int, int]]:
        configs = []
        max_r = max(r for r, c in shape)
        max_c = max(c for r, c in shape)

        for dr in range(self.size - max_r):
            for dc in range(self.size - max_c):
                placed = {(r + dr, c + dc) for r, c in shape}
                if placed.issubset(self.valid_cells):
                    configs.append(placed)
        return configs

    def get_all_pieces_configs(self) -> None:
        self.configs = {}
        for name, shape in PIECES.items():
            orientations = self.get_all_pieces_orientations(shape)
            configs = []
            for ori in orientations:
                configs.extend(self.generate_piece_configs(ori))
            self.configs[name] = {
                idx: config for idx, config in enumerate(configs)
            }
        return None

    def visualize(self) -> None:
        super().visualize()
        board = [[None] * self.size for _ in range(self.size)]
        board[self.day_cell[0]][self.day_cell[1]] = self.day
        board[self.month_cell[0]][self.month_cell[1]] = self.month
        for piece, configs in self.x_vars.items():
            for config, value in configs.items():
                if value.x == 0:
                    continue
                for cell in self.configs[piece][config]:
                    board[cell[0]][cell[1]] = piece
                break
        for row in range(self.size):
            render_up_row = f'{Colors.BOLD}{Colors.GRAY}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.GRAY}|{Colors.ENDC}'
            for col in range(self.size):
                if (row, col) == self.day_cell:
                    render_row += str(self.day).rjust(3)
                elif (row, col) == self.month_cell:
                    render_row += str(self.month).rjust(3)
                elif board[row][col] is not None:
                    render_row += f'{PIECES_COLOR[board[row][col]]}   {Colors.ENDC}'
                else:
                    render_row += f'   '
                if (
                    col == self.size - 1
                    or board[row][col] != board[row][col + 1]
                ):
                    render_row += f'{Colors.BOLD}{Colors.GRAY}|{Colors.ENDC}'
                    cross_node = f'{Colors.BOLD}{Colors.GRAY}+{Colors.ENDC}'
                else:
                    if board[row][col] is not None:
                        render_row += f'{PIECES_COLOR[board[row][col]]} {Colors.ENDC}'
                    else:
                        render_row += ' '

                if row == 0 or board[row][col] != board[row - 1][col]:
                    render_up_row += f'{Colors.BOLD}{Colors.GRAY}---+{Colors.ENDC}'
                else:
                    if board[row][col] is None:
                        continue
                    if col < self.size - 1 and (
                        board[row][col] == board[row][col + 1]
                    ) and (
                        board[row][col] == board[row - 1][col]
                    ) and (
                        board[row][col] == board[row - 1][col + 1]
                    ):
                        render_up_row += f'{PIECES_COLOR[board[row][col]]}    {Colors.ENDC}'
                    else:
                        render_up_row += f'{PIECES_COLOR[board[row][col]]}   {Colors.ENDC}{cross_node}'
            print(render_up_row)
            print(render_row)
        print(f'{Colors.BOLD}{Colors.GRAY}{"---".join(["+"] * (self.size + 1))}{Colors.ENDC}')