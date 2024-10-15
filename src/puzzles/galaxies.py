import itertools

from pathlib import Path

import mip
import networkx as nx


from src.model import BaseModel
from src.utils import Colors


class Galaxies(BaseModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        self.galaxy_number = len(self.data.galaxies)
        return None

    def verify_data(self) -> None:
        if self.data.galaxies == 0:
            raise ValueError('Puzzle must have at least 1 galaxy.')
        for galaxy in self.data.galaxies:
            if len(galaxy) not in [1, 2, 4]:
                raise ValueError(f'Galaxy center must be have 1, 2 or 4 cells, not {len(galaxy)}.')
            if len(set([(cell['row'], cell['col']) for cell in galaxy])) != len(galaxy):
                raise ValueError(f'Galaxy center have duplicate cell: {galaxy}.')
            min_row = min([cell['row'] for cell in galaxy])
            max_row = min([cell['row'] for cell in galaxy])
            min_col = min([cell['col'] for cell in galaxy])
            max_col = min([cell['col'] for cell in galaxy])
            if max_row - min_row > 1 or max_col - min_col > 1:
                raise ValueError(f'Invalid coordinate of galaxy{galaxy}')
        return None

    def init_model(self) -> None:
        for galaxy in range(self.galaxy_number):
            self.data.galaxies[galaxy] = sorted(
                self.data.galaxies[galaxy], key=lambda x: (x['row'], x['col'])
            )
        self.centers = [
            (
                sum([cell['row'] for cell in galaxy]) / len(galaxy),
                sum([cell['col'] for cell in galaxy]) / len(galaxy)
            ) for galaxy in self.data.galaxies
        ]
        self.get_galaxies_candidate_cells()
        super().init_model()
        return None

    def get_symetrical_cells(self, center, cell) -> tuple[int, int]:
        return (
            int(center[0] + center[0] - cell[0]),
            int(center[1] + center[1] - cell[1])
        )

    def get_galaxies_candidate_cells(self) -> None:
        all_centers_cells = [
            (cell['row'], cell['col'])
            for cell in sum(self.data.galaxies, start=[])
        ]

        self.galaxies_candidate_cells = [[] for _ in range(len(self.data.galaxies))]
        for galaxy, center in enumerate(self.centers):
            gap_row = min(center[0], self.data.shape[0] - 1 - center[0])
            gap_col = min(center[1], self.data.shape[1] - 1 - center[1])
            for row, col in itertools.product(
                range(int(center[0] - gap_row), self.data.galaxies[galaxy][0]['row'] + 1),
                range(int(center[1] - gap_col), int(center[1] + gap_col + 1))
            ):
                if (row, col) in all_centers_cells:
                    continue
                symetrical_cell = self.get_symetrical_cells(center, (row, col))
                if symetrical_cell in all_centers_cells:
                    continue
                self.galaxies_candidate_cells[galaxy].append((row, col))
                if symetrical_cell not in self.galaxies_candidate_cells[galaxy]:
                    self.galaxies_candidate_cells[galaxy].append(symetrical_cell)
        return None

    def get_cell_to_center_paths(self, graph, source) -> None:
        if source not in graph:
            raise nx.NodeNotFound(f"Source node {source} not in graph.")
        if 'center' not in graph:
            raise nx.NodeNotFound(f"Target node 'center' not in graph.")
        all_paths = nx.all_simple_paths(graph, source, 'center')
        result = []
        for path in all_paths:
            for cell in path:
                neighbor_cell_number_in_path = len([c for c in graph[cell] if c in path])
                if cell == source or cell == 'center':
                    if neighbor_cell_number_in_path >= 2:
                        break
                else:
                    if neighbor_cell_number_in_path >= 3:
                        break
            else:
                result.append(path)
        return result

    def add_variables(self) -> None:
        super().add_variables()
        self.x_vars = [[
            [
                self.add_variable(
                    vtype=mip.BINARY, name=f'x_{row}_{col}_{galaxy}'
                ) for galaxy in range(self.galaxy_number)
            ] for col in range(self.data.shape[1])
        ] for row in range(self.data.shape[0])]
        return None

    def add_constraints(self) -> None:
        super().add_constraints()
        self.add_each_cell_only_contained_in_one_galaxy_contraints()
        self.add_each_galaxy_contains_center_cells_contraints()
        self.add_galaxies_candidate_cells_constraints()
        self.add_symetrical_constraints()
        self.add_galaxy_shape_conected_constraints()
        return None

    def add_each_cell_only_contained_in_one_galaxy_contraints(self) -> None:
        for row, col in itertools.product(
            range(self.data.shape[0]), range(self.data.shape[1])
        ):
            self.add_constraint(
                mip.xsum(self.x_vars[row][col][galaxy] for galaxy in range(self.galaxy_number)) == 1
            )
        return None

    def add_each_galaxy_contains_center_cells_contraints(self) -> None:
        for index, center_cells in enumerate(self.data.galaxies):
            for cell in center_cells:
                for galaxy in range(self.galaxy_number):
                    if galaxy == index:
                        self.add_constraint(
                            self.x_vars[cell['row']][cell['col']][galaxy] == 1
                        )
                    else:
                        self.add_constraint(
                            self.x_vars[cell['row']][cell['col']][galaxy] == 0
                        )
        return None

    def add_galaxies_candidate_cells_constraints(self) -> None:
        for galaxy, candidate_cells in enumerate(self.galaxies_candidate_cells):
            for row, col in itertools.product(
                range(self.data.shape[0]), range(self.data.shape[1])
            ):
                if (row, col) not in candidate_cells + [
                    (cell['row'], cell['col']) for cell in self.data.galaxies[galaxy]
                ]:
                    self.add_constraint(
                        self.x_vars[row][col][galaxy] == 0
                    )
        return None

    def add_symetrical_constraints(self) -> None:
        for galaxy, cells in enumerate(self.galaxies_candidate_cells):
            for cell in cells:
                if cell[0] <= self.data.galaxies[galaxy][0]['row']:
                    symetrical_cell = self.get_symetrical_cells(self.centers[galaxy], cell)
                    self.add_constraint(
                        self.x_vars[cell[0]][cell[1]][galaxy]
                        == self.x_vars[symetrical_cell[0]][symetrical_cell[1]][galaxy]
                    )
        return None

    def create_candidate_cells_graph(self, candidate_cells: list[tuple], center_cells: list[dict]) -> nx.Graph:
        graph = nx.Graph()
        graph.add_node('center')
        for cell in candidate_cells:
            graph.add_node(cell)
        for cell in candidate_cells:
            if (cell[0] + 1, cell[1]) in candidate_cells:
                graph.add_edge(cell, (cell[0] + 1, cell[1]))
            if (cell[0], cell[1] + 1) in candidate_cells:
                graph.add_edge(cell, (cell[0], cell[1] + 1))
        for center_cell in center_cells:
            for cell in [
                (center_cell['row'] - 1, center_cell['col']),
                (center_cell['row'], center_cell['col'] - 1),
                (center_cell['row'] + 1, center_cell['col']),
                (center_cell['row'], center_cell['col'] + 1)
            ]:
                if cell in candidate_cells:
                    graph.add_edge(cell, 'center')
        return graph

    def add_galaxy_shape_conected_constraints(self) -> None:
        for galaxy in range(self.galaxy_number):
            if len(self.galaxies_candidate_cells[galaxy]) == 0:
                continue
            graph = self.create_candidate_cells_graph(
                self.galaxies_candidate_cells[galaxy], self.data.galaxies[galaxy]
            )
            for cell in self.galaxies_candidate_cells[galaxy]:
                if cell[0] <= self.data.galaxies[galaxy][0]['row']:
                    paths = self.get_cell_to_center_paths(graph, cell)
                    if len(paths) == 0:
                        self.add_constraint(
                            self.x_vars[cell[0]][cell[1]][galaxy] == 0
                        )
                        continue
                    temp_vars = [
                        self.add_variable(vtype=mip.BINARY) for _ in paths
                    ]
                    for index, path in enumerate(paths):
                        cells = path[1: len(path) - 1]
                        self.add_constraint(
                            mip.xsum(
                                self.x_vars[cell_in_path[0]][cell_in_path[1]][galaxy]
                                for cell_in_path in cells
                            ) >= len(cells) * temp_vars[index]
                        )
                        self.add_constraint(
                            mip.xsum(
                                self.x_vars[cell_in_path[0]][cell_in_path[1]][galaxy]
                                for cell_in_path in cells
                            ) + 1 <= temp_vars[index] + len(cells)
                        )
                    self.add_constraint(
                        self.x_vars[cell[0]][cell[1]][galaxy] <= mip.xsum(temp_vars)
                    )
        return None

    def visualize(self) -> None:
        super().visualize()
        galaxies_shapes = [[None] * self.data.shape[1] for _ in range(self.data.shape[0])]
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[1])):
            galaxies_shapes[row][col] = sum([
                galaxy*self.x_vars[row][col][galaxy].x
                for galaxy in range(self.galaxy_number)
            ])
        center_positions = {}
        for galaxy in self.data.galaxies:
            if len(galaxy) == 1:
                center_positions[galaxy[0]['row'], galaxy[0]['col']] = 'C'
            elif len(galaxy) == 2:
                if galaxy[0]['row'] == galaxy[1]['row']:
                    center_positions[galaxy[0]['row'], galaxy[0]['col']] = 'R'
                else:
                    center_positions[galaxy[1]['row'], galaxy[1]['col']] = 'U'
            elif len(galaxy) == 4:
                center_positions[galaxy[2]['row'], galaxy[2]['col']] = 'RU'

        def is_center_position(cell, postion):
            return (
                cell in center_positions.keys()
                and center_positions[(row, col)] == postion
            )

        for row in range(self.data.shape[0]):
            render_up_row = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            render_row = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if is_center_position((row, col), 'C'):
                    render_row += f'{Colors.GREEN} 𖤓 {Colors.ENDC}'
                else:
                    render_row += f'   '
                if (
                    col == self.data.shape[1] - 1
                    or galaxies_shapes[row][col] != galaxies_shapes[row][col + 1]
                ):
                    render_row += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    cross_node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    if is_center_position((row, col), 'R'):
                        render_row += f'{Colors.GREEN}𖤓{Colors.ENDC}'
                    else:
                        render_row += f' '
                    if is_center_position((row, col), 'RU'):
                        cross_node = f'{Colors.GREEN}𖤓{Colors.ENDC}'
                    else:
                        cross_node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0 or galaxies_shapes[row][col] != galaxies_shapes[row - 1][col]:
                    normal_cross_node = f'{Colors.GRAY}+{Colors.ENDC}'
                    if render_up_row.endswith(normal_cross_node):
                        render_up_row = render_up_row[:len(render_up_row) - len(normal_cross_node)]
                        render_up_row += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        render_up_row += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    if is_center_position((row, col), 'U'):
                        render_up_row += f' {Colors.GREEN}𖤓{Colors.ENDC} {cross_node}'
                    else:
                        render_up_row += f'   {cross_node}'
            print(render_up_row)
            print(render_row)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}')
        return None
