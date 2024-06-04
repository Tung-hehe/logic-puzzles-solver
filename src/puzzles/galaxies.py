import itertools

from pathlib import Path

import mip
import networkx as nx

from .model import Model

from src.utils import PuzzleName, Colors


class Galaxies(Model):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath, PuzzleName.Binox)
        self.nGalaxies = len(self.data['galaxies'])
        self.verifyData()
        return None

    def verifyData(self) -> None:
        if self.nGalaxies == 0:
            raise ValueError('Puzzle must have at least 1 galaxy.')
        for galaxy in self.data['galaxies']:
            if len(galaxy) not in [1, 2, 4]:
                raise ValueError(f'Galaxy center must be have 1, 2 or 4 cells, not {len(galaxy)}.')
            if len(set([(cell['row'], cell['col']) for cell in galaxy])) != len(galaxy):
                raise ValueError(f'Galaxy center have duplicate cell: {galaxy}.')
            minRow = min([cell['row'] for cell in galaxy])
            maxRow = min([cell['row'] for cell in galaxy])
            minCol = min([cell['col'] for cell in galaxy])
            maxCol = min([cell['col'] for cell in galaxy])
            if maxRow - minRow > 1 or maxCol - minCol > 1:
                raise ValueError(f'Invalid coordinate of galaxy{galaxy}')
        return None

    def initModel(self) -> None:
        for galaxy in range(self.nGalaxies):
            self.data['galaxies'][galaxy] = sorted(
                self.data['galaxies'][galaxy], key=lambda x: (x['row'], x['col'])
            )
        self.centers = [
            (
                sum([cell['row'] for cell in galaxy]) / len(galaxy),
                sum([cell['col'] for cell in galaxy]) / len(galaxy)
            ) for galaxy in self.data['galaxies']
        ]
        self.findAllCandidateCellOfGalaxies()
        super().initModel()
        return None

    def findSymetricalCell(self, center, cell) -> tuple[int, int]:
        return (
            int(center[0] + center[0] - cell[0]),
            int(center[1] + center[1] - cell[1])
        )

    def findAllCandidateCellOfGalaxies(self) -> None:
        allCentersCells = [
            (cell['row'], cell['col'])
            for cell in sum(self.data['galaxies'], start=[])
        ]

        self.candidateCellsOfGalaxies = [[] for _ in range(len(self.data['galaxies']))]
        for galaxy, center in enumerate(self.centers):
            gapRow = min(center[0], self.data['shape'][0] - 1 - center[0])
            gapCol = min(center[1], self.data['shape'][1] - 1 - center[1])
            for row, col in itertools.product(
                range(int(center[0] - gapRow), self.data['galaxies'][galaxy][0]['row'] + 1),
                range(int(center[1] - gapCol), int(center[1] + gapCol + 1))
            ):
                if (row, col) in allCentersCells:
                    continue
                symetricalCell = self.findSymetricalCell(center, (row, col))
                if symetricalCell in allCentersCells:
                    continue
                self.candidateCellsOfGalaxies[galaxy].append((row, col))
                if symetricalCell not in self.candidateCellsOfGalaxies[galaxy]:
                    self.candidateCellsOfGalaxies[galaxy].append(symetricalCell)
        return None

    def findAllPathsFromCellToCenter(self, graph, source) -> None:
        if source not in graph:
            raise nx.NodeNotFound(f"Source node {source} not in graph.")
        if 'center' not in graph:
            raise nx.NodeNotFound(f"Target node 'center' not in graph.")
        allPaths = nx.all_simple_paths(graph, source, 'center')
        result = []
        for path in allPaths:
            for cell in path:
                nNeighborsInPath = len([c for c in graph[cell] if c in path])
                if cell == source or cell == 'center':
                    if nNeighborsInPath >= 2:
                        break
                else:
                    if nNeighborsInPath >= 3:
                        break
            else:
                result.append(path)
        return result

    def addVariables(self) -> None:
        super().addVariables()
        self.xVars = [
            [
                [
                    self.addVariable(vtype=mip.BINARY, name=f'x_{row}_{col}_{galaxy}')
                    for galaxy in range(self.nGalaxies)
                ] for col in range(self.data['shape'][1])
            ] for row in range(self.data['shape'][0])
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addEachCellOnlyContaintInOneGalaxy()
        self.addCenterCellsContaintInGalaxies()
        self.addCandidateCellsOfGalaxiesConstraint()
        self.addSymetricalConstraints()
        self.addGalaxyShapeConectedConstraints()
        return None

    def addEachCellOnlyContaintInOneGalaxy(self) -> None:
        for row, col in itertools.product(
            range(self.data['shape'][0]), range(self.data['shape'][1])
        ):
            self.addConstraint(
                mip.xsum(self.xVars[row][col][galaxy] for galaxy in range(self.nGalaxies)) == 1
            )
        return None

    def addCenterCellsContaintInGalaxies(self) -> None:
        for index, centersCell in enumerate(self.data['galaxies']):
            for cell in centersCell:
                for galaxy in range(self.nGalaxies):
                    if galaxy == index:
                        self.addConstraint(
                            self.xVars[cell['row']][cell['col']][galaxy] == 1
                        )
                    else:
                        self.addConstraint(
                            self.xVars[cell['row']][cell['col']][galaxy] == 0
                        )
        return None

    def addCandidateCellsOfGalaxiesConstraint(self) -> None:
        for galaxy, candidateCells in enumerate(self.candidateCellsOfGalaxies):
            for row, col in itertools.product(
                range(self.data['shape'][0]), range(self.data['shape'][1])
            ):
                if (row, col) not in candidateCells + [
                    (cell['row'], cell['col']) for cell in self.data['galaxies'][galaxy]
                ]:
                    self.addConstraint(
                        self.xVars[row][col][galaxy] == 0
                    )
        return None

    def addSymetricalConstraints(self) -> None:
        for galaxy, cells in enumerate(self.candidateCellsOfGalaxies):
            for cell in cells:
                if cell[0] <= self.data['galaxies'][galaxy][0]['row']:
                    symetricalCell = self.findSymetricalCell(self.centers[galaxy], cell)
                    self.addConstraint(
                        self.xVars[cell[0]][cell[1]][galaxy]
                        == self.xVars[symetricalCell[0]][symetricalCell[1]][galaxy]
                    )
        return None

    def addGalaxyShapeConectedConstraints(self) -> None:
        for galaxy in range(self.nGalaxies):
            if len(self.candidateCellsOfGalaxies[galaxy]) == 0:
                continue
            graph = nx.Graph()
            graph.add_node('center')
            for cell in self.candidateCellsOfGalaxies[galaxy]:
                graph.add_node(cell)
            for cell in self.candidateCellsOfGalaxies[galaxy]:
                if (cell[0] + 1, cell[1]) in self.candidateCellsOfGalaxies[galaxy]:
                    graph.add_edge(cell, (cell[0] + 1, cell[1]))
                if (cell[0], cell[1] + 1) in self.candidateCellsOfGalaxies[galaxy]:
                    graph.add_edge(cell, (cell[0], cell[1] + 1))
            for centerCell in self.data['galaxies'][galaxy]:
                for cell in [
                    (centerCell['row'] - 1, centerCell['col']),
                    (centerCell['row'], centerCell['col'] - 1),
                    (centerCell['row'] + 1, centerCell['col']),
                    (centerCell['row'], centerCell['col'] + 1)
                ]:
                    if cell in self.candidateCellsOfGalaxies[galaxy]:
                        graph.add_edge(cell, 'center')
            for cell in self.candidateCellsOfGalaxies[galaxy]:
                if cell[0] <= self.data['galaxies'][galaxy][0]['row']:
                    paths = self.findAllPathsFromCellToCenter(graph, cell)
                    if len(paths) == 0:
                        self.addConstraint(
                            self.xVars[cell[0]][cell[1]][galaxy] == 0
                        )
                        continue
                    tempVars = [
                        self.addVariable(vtype=mip.BINARY) for _ in paths
                    ]
                    for index, path in enumerate(paths):
                        cells = path[1: len(path) - 1]
                        self.addConstraint(
                            mip.xsum(
                                self.xVars[cellInPath[0]][cellInPath[1]][galaxy]
                                for cellInPath in cells
                            ) >= len(cells) * tempVars[index]
                        )
                        self.addConstraint(
                            mip.xsum(
                                self.xVars[cellInPath[0]][cellInPath[1]][galaxy]
                                for cellInPath in cells
                            ) + 1 <= tempVars[index] + len(cells)
                        )
                    self.addConstraint(
                        self.xVars[cell[0]][cell[1]][galaxy] <= mip.xsum(tempVars)
                    )
        return None

    def visualize(self) -> None:
        super().visualize()
        galaxiesShapes = [[None] * self.data['shape'][1] for _ in range(self.data['shape'][0])]
        for row, col in itertools.product(
            range(self.data['shape'][0]),
            range(self.data['shape'][1])
        ):
            galaxiesShapes[row][col] = sum([
                galaxy*self.xVars[row][col][galaxy].x for galaxy in range(self.nGalaxies)
            ])
        centersPositions = {}
        for galaxy in self.data['galaxies']:
            if len(galaxy) == 1:
                centersPositions[galaxy[0]['row'], galaxy[0]['col']] = 'C'
            elif len(galaxy) == 2:
                if galaxy[0]['row'] == galaxy[1]['row']:
                    centersPositions[galaxy[0]['row'], galaxy[0]['col']] = 'R'
                else:
                    centersPositions[galaxy[1]['row'], galaxy[1]['col']] = 'U'
            elif len(galaxy) == 4:
                centersPositions[galaxy[2]['row'], galaxy[2]['col']] = 'RU'

        def checkCenterPosition(cell, postion):
            return (
                cell in centersPositions.keys()
                and centersPositions[(row, col)] == postion
            )
        for row in range(self.data['shape'][0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data['shape'][1]):
                if checkCenterPosition((row, col), 'C'):
                    renderRow += f'{Colors.GREEN} 𖤓 {Colors.ENDC}'
                else:
                    renderRow += f'   '
                if (
                    col == self.data['shape'][1] - 1
                    or galaxiesShapes[row][col] != galaxiesShapes[row][col + 1]
                ):
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    crossNode = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    if checkCenterPosition((row, col), 'R'):
                        renderRow += f'{Colors.GREEN}𖤓{Colors.ENDC}'
                    else:
                        renderRow += f' '
                    if checkCenterPosition((row, col), 'RU'):
                        crossNode = f'{Colors.GREEN}𖤓{Colors.ENDC}'
                    else:
                        crossNode = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0 or galaxiesShapes[row][col] != galaxiesShapes[row - 1][col]:
                    normalCrossNode = f'{Colors.GRAY}+{Colors.ENDC}'
                    if renderUpRow.endswith(normalCrossNode):
                        renderUpRow = renderUpRow[:len(renderUpRow) - len(normalCrossNode)]
                        renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    if checkCenterPosition((row, col), 'U'):
                        renderUpRow += f' {Colors.GREEN}𖤓{Colors.ENDC} {crossNode}'
                    else:
                        renderUpRow += f'   {crossNode}'
            print(renderUpRow)
            print(renderRow)
        print(f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data["shape"][1] + 1))}{Colors.ENDC}')
        return None
