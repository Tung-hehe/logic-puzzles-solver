from pathlib import Path


from src.model import LineModel
from src.utils import Colors


class Slitherlink(LineModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verify_data(self) -> None:
        for cell in self.data.surrounded_line_number:
            if (
                0 > cell['row'] or cell['row'] >= self.data.shape[0]
                or 0 > cell['col'] or cell['col'] >= self.data.shape[1]
            ):
                raise ValueError(f'Cell ({cell}) has invalid coordinate')
            if cell['val'] >= 4:
                raise ValueError(f'Cell ({cell}) has invalid value. Value must be less than 4')
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_surround_lines_numnber_constraints()
        return None

    def add_surround_lines_numnber_constraints(self) -> None:
        for cell in self.data.surrounded_line_number:
            self.add_constraint(
                self.h_vars[cell['row']][cell['col']]
                + self.h_vars[cell['row'] + 1][cell['col']]
                + self.v_vars[cell['row']][cell['col']]
                + self.v_vars[cell['row']][cell['col'] + 1]
                == cell['val']
            )
        return None

    def get_rendered_lines_in_main_board(self) -> list[str]:
        rendered_lines = []
        surround_cells = {
            (cell['row'], cell['col']): cell['val'] for cell in self.data.surrounded_line_number
        }
        h_lines = []
        normal_node = f'{Colors.GRAY}+{Colors.ENDC}'
        for row in range(self.data.shape[0] + 1):
            if self.h_vars[row][0].x == 1:
                h_line = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            else:
                if (
                    (row < self.data.shape[0] and self.v_vars[row][0].x == 1)
                    or (row > 0 and self.v_vars[row - 1][0].x == 1)
                ):
                    h_line = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    h_line = f'{Colors.BOLD}{normal_node}'
            for col in range(self.data.shape[1]):
                if self.h_vars[row][col].x == 1:
                    if h_line.endswith(normal_node):
                        h_line = h_line[:len(h_line) - len(normal_node)]
                        h_line += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        h_line += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    if (
                        (row < self.data.shape[0] and self.v_vars[row][col + 1].x == 1)
                        or (row > 0 and self.v_vars[row - 1][col + 1].x == 1)
                    ):
                        h_line += f'   {Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                    else:
                        h_line += f'   {normal_node}'
            h_lines.append(h_line)
        v_lines = []
        for row in range(self.data.shape[0]):
            if self.v_vars[row][0].x == 1:
                v_line = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            else:
                v_line = f'{Colors.BOLD}{Colors.GRAY} {Colors.GRAY}'
            for col in range(1, self.data.shape[1] + 1):
                if self.v_vars[row][col].x == 1:
                    line = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                else:
                    line = f' '
                if (row, col - 1) in surround_cells.keys():
                    val = f' {Colors.BOLD}{Colors.GREEN}{surround_cells[(row, col - 1)]}{Colors.ENDC} '
                else:
                    val = f'   '
                v_line += val + line
            v_lines.append(v_line)
        for row in range(self.data.shape[0]):
            rendered_lines.append(h_lines[row])
            rendered_lines.append(v_lines[row])
        rendered_lines.append(h_lines[row + 1])
        return rendered_lines

    def visualize(self) -> None:
        super().visualize()
        rendered_lines_in_main_board = self.get_rendered_lines_in_main_board()
        temp_line = f"{Colors.GRAY}+{'-'*((self.data.shape[1] + 2)*4 - 1)}+{Colors.ENDC}"
        temp_row = f"{Colors.GRAY}|{' '*((self.data.shape[1] + 2)*4 - 1)}|{Colors.ENDC}"
        print(temp_line)
        print(temp_row)
        for l in rendered_lines_in_main_board:
            print(f'{Colors.GRAY}|{Colors.ENDC}   {l}   {Colors.GRAY}|{Colors.ENDC}')
        print(temp_row)
        print(temp_line)
        return None
