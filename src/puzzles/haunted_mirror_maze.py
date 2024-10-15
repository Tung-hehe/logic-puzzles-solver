import itertools

from pathlib import Path

import mip


from src.model import BaseModel
from src.utils import Colors
from src.utils import (
    Position,
    Mirror,
    Monster,
)


class HauntedMirrorMaze(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.change_direction = {
            ((Position.Top, Position.Bottom), Mirror.RightDownToLeft): (Position.Right, Position.Left),
            ((Position.Top, Position.Bottom), Mirror.LeftDownToRight): (Position.Left, Position.Right),
            ((Position.Bottom, Position.Top), Mirror.RightDownToLeft): (Position.Left, Position.Right),
            ((Position.Bottom, Position.Top), Mirror.LeftDownToRight): (Position.Right, Position.Left),
            ((Position.Left, Position.Right), Mirror.RightDownToLeft): (Position.Bottom, Position.Top),
            ((Position.Left, Position.Right), Mirror.LeftDownToRight): (Position.Top, Position.Bottom),
            ((Position.Right, Position.Left), Mirror.RightDownToLeft): (Position.Top, Position.Bottom),
            ((Position.Right, Position.Left), Mirror.LeftDownToRight): (Position.Bottom, Position.Top),
        }
        self.move_direction = {
            (Position.Bottom, Position.Top): (-1, 0),
            (Position.Top, Position.Bottom): (1, 0),
            (Position.Right, Position.Left): (0, -1),
            (Position.Left, Position.Right): (0, 1),
        }
        self.convert_data()
        return None

    def verify_data(self) -> None:
        for mirror in self.data.mirrors:
            if mirror['row'] >= self.data.shape[0] or mirror['col'] >= self.data.shape[1]:
                raise ValueError(f'Mirror {mirror} is out of range.')
            if mirror['val'] not in ['\\', '/']:
                raise ValueError(f'Invalid mirror type {mirror["val"]}.')
        for cell in self.data.fixed_cells:
            if cell['row'] >= self.data.shape[0] or cell['col'] >= self.data.shape[1]:
                raise ValueError(f'Cell {cell} is out of range.')
            if cell['val'] not in ['V', 'G', 'Z']:
                raise ValueError(f'Invalid monster type {cell["val"]}')
        if len(self.data.monster_number) > 3:
            raise ValueError(f'monster_number should have less than 3 elements.')
        monsters = []
        total = []
        for monster in self.data.monster_number:
            if monster['name'] not in ['V', 'G', 'Z']:
                raise ValueError(f'Invalid monster type {cell["val"]}.')
            monsters.append(monster['name'])
            total.append(monster['val'])
        if len(set(monsters)) != len(monsters):
            raise ValueError(f'Monsters are duplicate.')
        if sum(total) > self.data.shape[0] * self.data.shape[1] - len(self.data.mirrors):
            raise ValueError(f'Too much monsters to fill in puzzle.')
        return None

    def convert_data(self) -> None:
        self.data.visibility = {
            Position(position): visibility for position, visibility in self.data.visibility.items()
        }
        self.data.mirrors = {
            (cell['row'], cell['col']): Mirror(cell['val'])
            for cell in self.data.mirrors
        }
        self.data.monster_number = [
            {'name': Monster(cell['name']), 'val': cell['val']}
            for cell in self.data.monster_number
        ]
        self.data.fixed_cells = [
            {'row': cell['row'], 'col': cell['col'], 'val': Monster(cell['val'])}
            for cell in self.data.fixed_cells
        ]
        return None

    def add_variables(self) -> None:
        super().add_variables()
        self.v_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        self.g_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'g_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        self.z_vars = [
            [
                self.add_variable(vtype=mip.BINARY, name=f'z_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_mirror_cell_not_contain_monster_constraints()
        self.add_each_cell_contains_one_monster_constraints()
        self.add_fixed_cells_constraints()
        self.add_same_cells_constraints()
        self.add_limit_monster_number_constraints()
        self.add_visible_monster_number_constraints()
        return None

    def add_mirror_cell_not_contain_monster_constraints(self) -> None:
        for row, col in self.data.mirrors.keys():
            self.add_constraint(self.v_vars[row][col] == 0)
            self.add_constraint(self.g_vars[row][col] == 0)
            self.add_constraint(self.z_vars[row][col] == 0)
        return None

    def add_each_cell_contains_one_monster_constraints(self) -> None:
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[1])):
            if (row, col) not in self.data.mirrors.keys():
                self.add_constraint(
                    self.v_vars[row][col] + self.g_vars[row][col] + self.z_vars[row][col] == 1
                )
        return None

    def add_fixed_cells_constraints(self) -> None:
        for cell in self.data.fixed_cells:
            match cell['val']:
                case Monster.Vampire:
                    self.add_constraint(self.v_vars[cell['row']][cell['col']] == 1)
                case Monster.Ghost:
                    self.add_constraint(self.g_vars[cell['row']][cell['col']] == 1)
                case Monster.Zombie:
                    self.add_constraint(self.z_vars[cell['row']][cell['col']] == 1)
                case _:
                    raise ValueError(f'Invalid monster {cell["val"]}')
        return None

    def add_same_cells_constraints(self) -> None:
        if len(self.data.same_cells):
            for i in range(1, len(self.data.same_cells)):
                self.add_constraint(
                    self.v_vars[self.data.same_cells[i]['row']][self.data.same_cells[i]['col']]
                    == self.v_vars[self.data.same_cells[0]['row']][self.data.same_cells[0]['col']]
                )
                self.add_constraint(
                    self.g_vars[self.data.same_cells[i]['row']][self.data.same_cells[i]['col']]
                    == self.g_vars[self.data.same_cells[0]['row']][self.data.same_cells[0]['col']]
                )
                self.add_constraint(
                    self.z_vars[self.data.same_cells[i]['row']][self.data.same_cells[i]['col']]
                    == self.z_vars[self.data.same_cells[0]['row']][self.data.same_cells[0]['col']]
                )
        return None

    def add_limit_monster_number_constraints(self) -> None:
        for monster_number in self.data.monster_number:
            match monster_number['name']:
                case Monster.Vampire:
                    self.add_constraint(mip.xsum(
                        self.v_vars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == monster_number['val'])
                case Monster.Ghost:
                    self.add_constraint(mip.xsum(
                        self.g_vars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == monster_number['val'])
                case Monster.Zombie:
                    self.add_constraint(mip.xsum(
                        self.z_vars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == monster_number['val'])
                case _:
                    raise ValueError(f'Invalid monster {monster_number["name"]}')
        return None

    def add_visible_monster_number_constraints(self) -> None:
        for position, visible_monster_number_list in self.data.visibility.items():
            for cell_index, monster_number in enumerate(visible_monster_number_list):
                if monster_number is  None:
                    continue
                head_on_cells, reflective_cells = self.get_visible_cells(position, cell_index)
                self.add_constraint(
                    mip.xsum(
                        self.v_vars[row][col] + self.z_vars[row][col]
                        for row, col in head_on_cells
                    ) + mip.xsum(
                        self.g_vars[row][col] + self.z_vars[row][col]
                        for row, col in reflective_cells
                    ) == monster_number
                )
        return None

    def is_on_board(self, cell: tuple) -> bool:
        if (
            cell[0] < 0 or cell [0] >= self.data.shape[0]
            or cell[1] < 0 or cell [1] >= self.data.shape[1]
        ):
            return False
        return True

    def get_visible_cells(self, position: Position, cell_index: int) -> tuple[list, list]:
        match position:
            case Position.Top:
                start_cell = (0, cell_index)
                current_direction = (Position.Top, Position.Bottom)
            case Position.Bottom:
                start_cell = (self.data.shape[0] - 1, cell_index)
                current_direction = (Position.Bottom, Position.Top)
            case Position.Left:
                start_cell = (cell_index, 0)
                current_direction = (Position.Left, Position.Right)
            case Position.Right:
                start_cell = (cell_index, self.data.shape[1] - 1)
                current_direction = (Position.Right, Position.Left)
            case _:
                raise ValueError(f'Invalide position {position}')
        reflect = False
        head_on_cells = []
        reflective_cells = []
        current_cell = start_cell
        while self.is_on_board(current_cell):
            if current_cell in self.data.mirrors.keys():
                reflect = True
                current_direction = self.change_direction[
                    (current_direction, self.data.mirrors[current_cell])
                ]
            else:
                if reflect:
                    reflective_cells.append(current_cell)
                else:
                    head_on_cells.append(current_cell)
            current_cell = (
                current_cell[0] + self.move_direction[current_direction][0],
                current_cell[1] + self.move_direction[current_direction][1]
            )
        return head_on_cells, reflective_cells

    def get_rendered_lines_in_main_board(self) -> list[str]:
        rendered_lines = []
        for row in range(self.data.shape[0]):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if (row, col) in self.data.mirrors.keys():
                    if self.data.mirrors[(row, col)] == Mirror.LeftDownToRight:
                        render_row += f' {Colors.BOLD}{Colors.BLUE}\\{Colors.ENDC} '
                    elif self.data.mirrors[(row, col)] == Mirror.RightDownToLeft:
                        render_row += f' {Colors.BOLD}{Colors.BLUE}/{Colors.ENDC} '
                    else:
                        raise ValueError(f'Invalid mirror {self.data.mirrors[(row, col)]}')
                else:
                    if self.v_vars[row][col].x == 1:
                        render_row += f' {Colors.BOLD}{Colors.RED}V{Colors.ENDC} '
                    elif self.g_vars[row][col].x == 1:
                        render_row += f' {Colors.BOLD}{Colors.YELLOW}G{Colors.ENDC} '
                    elif self.z_vars[row][col].x == 1:
                        render_row += f' {Colors.BOLD}{Colors.GREEN}Z{Colors.ENDC} '
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
            rendered_lines.append(render_up_row)
            rendered_lines.append(render_row)
        rendered_lines.append(
            f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}'
        )
        return rendered_lines

    def visualize(self) -> None:
        super().visualize()
        rendered_lines_in_main_board = self.get_rendered_lines_in_main_board()
        topLine = f'{Colors.GRAY}    '
        for cell in self.data.visibility[Position.Top]:
            if cell is None:
                topLine += '    '
            else:
                topLine += str(cell).center(4)
        topLine += f'{Colors.ENDC}'
        print(topLine)
        for i, l in enumerate(rendered_lines_in_main_board):
            if i % 2:
                left_number = self.data.visibility[Position.Left][int(i/2)]
                if left_number is None: left_number = '   '
                else: left_number = str(left_number).center(3)

                right_number = self.data.visibility[Position.Right][int(i/2)]
                if right_number is None: right_number = '   '
                else: right_number = str(right_number).center(3)

                print(f'{Colors.GRAY}{left_number}{Colors.ENDC}{l}{Colors.GRAY}{right_number}{Colors.ENDC}')
            else:
                print(f'   {l}    ')
        bottom_line = f'{Colors.GRAY}    '
        for cell in self.data.visibility[Position.Bottom]:
            if cell is None:
                bottom_line += '    '
            else:
                bottom_line += str(cell).center(4)
        bottom_line += f'{Colors.ENDC}'
        print(bottom_line)
        return None
