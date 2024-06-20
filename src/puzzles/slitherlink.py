import itertools

from pathlib import Path

import mip


from src.model import LineModel
from src.utils import Colors


class Slitherlink(LineModel):

    def __init__(self, dataPath: Path) -> None:
        super().__init__(dataPath)
        return None

    def verifyData(self) -> None:
        for cell in self.data['nLinesSurround']:
            if (
                0 < cell['row'] or cell['row'] >= self.data['shape'][0]
                or 0 < cell['col'] or cell['col'] >= self.data['shape'][1]
            ):
                raise ValueError(f'Cell ({cell}) has invalid coordinate')
            if cell['val'] >= 4:
                raise ValueError(f'Cell ({cell}) has invalid value. Value must be less than 4')
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addNumberLinesSurroundConstraints()
        return None

    def addNumberLinesSurroundConstraints(self) -> None:
        for cell in self.data['nLinesSurround']:
            self.addConstraint(
                self.hVars[cell['row']][cell['col']]
                + self.hVars[cell['row'] + 1][cell['col']]
                + self.vVars[cell['row']][cell['col']]
                + self.vVars[cell['row']][cell['col'] + 1]
                == cell['val']
            )
        return None

    def getRenderedLinesInMainBoard(self) -> list[str]:
        renderedLines = []
        nLinesSurroundCells = {
            (cell['row'], cell['col']): cell['val'] for cell in self.data['nLinesSurround']
        }
        hLines = []
        normalNode = f'{Colors.GRAY}+{Colors.ENDC}'
        for row in range(self.data['shape'][0] + 1):
            if self.hVars[row][0].x == 1:
                hLine = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            else:
                if (
                    (row < self.data['shape'][0] and self.vVars[row][0].x == 1)
                    or (row > 0 and self.vVars[row - 1][0].x == 1)
                ):
                    hLine = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    hLine = f'{Colors.BOLD}{normalNode}'
            for col in range(self.data['shape'][1]):
                if self.hVars[row][col].x == 1:
                    if hLine.endswith(normalNode):
                        hLine = hLine[:len(hLine) - len(normalNode)]
                        hLine += f'{Colors.BOLD}{Colors.PURPLE}+---+{Colors.ENDC}'
                    else:
                        hLine += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    if (
                        (row < self.data['shape'][0] and self.vVars[row][col + 1].x == 1)
                        or (row > 0 and self.vVars[row - 1][col + 1].x == 1)
                    ):
                        hLine += f'   {Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                    else:
                        hLine += f'   {normalNode}'
            hLines.append(hLine)
        vLines = []
        for row in range(self.data['shape'][0]):
            if self.vVars[row][0].x == 1:
                vLine = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            else:
                vLine = f'{Colors.BOLD}{Colors.GRAY} {Colors.GRAY}'
            for col in range(1, self.data['shape'][1] + 1):
                if self.vVars[row][col].x == 1:
                    line = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                else:
                    line = f' '
                if (row, col - 1) in nLinesSurroundCells.keys():
                    val = f' {Colors.BOLD}{Colors.GREEN}{nLinesSurroundCells[(row, col - 1)]}{Colors.ENDC} '
                else:
                    val = f'   '
                vLine += val + line
            vLines.append(vLine)
        for row in range(self.data['shape'][0]):
            renderedLines.append(hLines[row])
            renderedLines.append(vLines[row])
        renderedLines.append(hLines[row + 1])
        return renderedLines

    def visualize(self) -> None:
        super().visualize()
        renderedLinesInMainBoard = self.getRenderedLinesInMainBoard()
        tempLine = f"{Colors.GRAY}+{'-'*((self.data['shape'][1] + 2)*4 - 1)}+{Colors.ENDC}"
        tempRow = f"{Colors.GRAY}|{' '*((self.data['shape'][1] + 2)*4 - 1)}|{Colors.ENDC}"
        print(tempLine)
        print(tempRow)
        for l in renderedLinesInMainBoard:
            print(f'{Colors.GRAY}|{Colors.ENDC}   {l}   {Colors.GRAY}|{Colors.ENDC}')
        print(tempRow)
        print(tempLine)
        return None
