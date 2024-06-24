import itertools

from enum import Enum
from pathlib import Path

import mip
import networkx as nx


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
        self.changeDirection = {
            ((Position.Top, Position.Bottom), Mirror.RightDownToLeft): (Position.Right, Position.Left),
            ((Position.Top, Position.Bottom), Mirror.LeftDownToRight): (Position.Left, Position.Right),
            ((Position.Bottom, Position.Top), Mirror.RightDownToLeft): (Position.Left, Position.Right),
            ((Position.Bottom, Position.Top), Mirror.LeftDownToRight): (Position.Right, Position.Left),
            ((Position.Left, Position.Right), Mirror.RightDownToLeft): (Position.Bottom, Position.Top),
            ((Position.Left, Position.Right), Mirror.LeftDownToRight): (Position.Top, Position.Bottom),
            ((Position.Right, Position.Left), Mirror.RightDownToLeft): (Position.Top, Position.Bottom),
            ((Position.Right, Position.Left), Mirror.LeftDownToRight): (Position.Bottom, Position.Top),
        }
        self.moveByDirection = {
            (Position.Bottom, Position.Top): (-1, 0),
            (Position.Top, Position.Bottom): (1, 0),
            (Position.Right, Position.Left): (0, -1),
            (Position.Left, Position.Right): (0, 1),
        }
        self.convertData()
        return None

    def verifyData(self) -> None:
        for mirror in self.data.mirrors:
            if mirror['row'] >= self.data.shape[0] or mirror['col'] >= self.data.shape[1]:
                raise ValueError(f'Mirror {mirror} is out of range.')
            if mirror['val'] not in ['\\', '/']:
                raise ValueError(f'Invalid mirror type {mirror["val"]}.')
        for cell in self.data.fixedCells:
            if cell['row'] >= self.data.shape[0] or cell['col'] >= self.data.shape[1]:
                raise ValueError(f'Cell {cell} is out of range.')
            if cell['val'] not in ['V', 'G', 'Z']:
                raise ValueError(f'Invalid monster type {cell["val"]}')
        if len(self.data.nMonsters) > 3:
            raise ValueError(f'nMonsters should have less than 3 elements.')
        monsters = []
        total = []
        for monster in self.data.nMonsters:
            if monster['name'] not in ['V', 'G', 'Z']:
                raise ValueError(f'Invalid monster type {cell["val"]}.')
            monsters.append(monster['name'])
            total.append(monster['val'])
        if len(set(monsters)) != len(monsters):
            raise ValueError(f'Monsters are duplicate.')
        if sum(total) >= self.data.shape[0] * self.data.shape[1] - len(self.data.mirrors):
            raise ValueError(f'Too much monsters to fill in puzzle.')
        return None

    def convertData(self) -> None:
        self.data.visibility = {
            Position(positionm): visibility for positionm, visibility in self.data.visibility.items()
        }
        self.data.mirrors = {
            (cell['row'], cell['col']): Mirror(cell['val'])
            for cell in self.data.mirrors
        }
        self.data.nMonsters = [
            {'name': Monster(cell['name']), 'val': cell['val']}
            for cell in self.data.nMonsters
        ]
        self.data.fixedCells = [
            {'row': cell['row'], 'col': cell['col'], 'val': Monster(cell['val'])}
            for cell in self.data.fixedCells
        ]
        return None

    def addVariables(self) -> None:
        super().addVariables()
        self.vVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        self.gVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        self.zVars = [
            [
                self.addVariable(vtype=mip.BINARY, name=f'v_{row}_{col}')
                for col in range(self.data.shape[1])
            ] for row in range(self.data.shape[0])
        ]
        return None

    def addConstraints(self) -> None:
        super().addConstraints()
        self.addMirrorCellNotContainMonster()
        self.addEachCellContaintOneMonsterConstraints()
        self.addFixedCellsConstraints()
        self.addSameCellsConstraints()
        self.addLimitMonstersConstraints()
        self.addVisibleMonstersConstraints()
        return None

    def addMirrorCellNotContainMonster(self) -> None:
        for row, col in self.data.mirrors.keys():
            self.addConstraint(self.vVars[row][col] == 0)
            self.addConstraint(self.gVars[row][col] == 0)
            self.addConstraint(self.zVars[row][col] == 0)
        return None

    def addEachCellContaintOneMonsterConstraints(self) -> None:
        for row, col in itertools.product(range(self.data.shape[0]), range(self.data.shape[1])):
            if (row, col) not in self.data.mirrors.keys():
                self.addConstraint(
                    self.vVars[row][col] + self.gVars[row][col] + self.zVars[row][col] == 1
                )
        return None

    def addFixedCellsConstraints(self) -> None:
        for cell in self.data.fixedCells:
            match cell['val']:
                case Monster.Vampire:
                    self.addConstraint(self.vVars[cell['row']][cell['col']] == 1)
                case Monster.Ghost:
                    self.addConstraint(self.gVars[cell['row']][cell['col']] == 1)
                case Monster.Zombie:
                    self.addConstraint(self.zVars[cell['row']][cell['col']] == 1)
                case _:
                    raise ValueError(f'Invalid monster {cell["val"]}')
        return None

    def addSameCellsConstraints(self) -> None:
        if len(self.data.sameCells):
            for i in range(1, len(self.data.sameCells)):
                self.addConstraint(
                    self.vVars[self.data.sameCells[i]['row']][self.data.sameCells[i]['col']]
                    == self.vVars[self.data.sameCells[0]['row']][self.data.sameCells[0]['col']]
                )
                self.addConstraint(
                    self.gVars[self.data.sameCells[i]['row']][self.data.sameCells[i]['col']]
                    == self.gVars[self.data.sameCells[0]['row']][self.data.sameCells[0]['col']]
                )
                self.addConstraint(
                    self.zVars[self.data.sameCells[i]['row']][self.data.sameCells[i]['col']]
                    == self.zVars[self.data.sameCells[0]['row']][self.data.sameCells[0]['col']]
                )
        return None

    def addLimitMonstersConstraints(self) -> None:
        for nMonsters in self.data.nMonsters:
            match nMonsters['name']:
                case Monster.Vampire:
                    self.addConstraint(mip.xsum(
                        self.vVars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == nMonsters['val'])
                case Monster.Ghost:
                    self.addConstraint(mip.xsum(
                        self.gVars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == nMonsters['val'])
                case Monster.Zombie:
                    self.addConstraint(mip.xsum(
                        self.zVars[row][col]
                        for row, col in itertools.product(
                            range(self.data.shape[0]), range(self.data.shape[1])
                        ) if (row, col) not in self.data.mirrors.keys()
                    ) == nMonsters['val'])
                case _:
                    raise ValueError(f'Invalid monster {nMonsters["name"]}')
        return None

    def addVisibleMonstersConstraints(self) -> None:
        for position, visibleMonstersList in self.data.visibility.items():
            for indexCell, nMonsters in enumerate(visibleMonstersList):
                headOnCells, reflectionCells = self.findVisibleCells(position, indexCell)
                self.addConstraint(
                    mip.xsum(
                        self.vVars[row][col] + self.zVars[row][col]
                        for row, col in headOnCells
                    ) + mip.xsum(
                        self.gVars[row][col] + self.zVars[row][col]
                        for row, col in reflectionCells
                    ) == nMonsters
                )
        return None

    def isOnBoard(self, cell: tuple) -> bool:
        if (
            cell[0] < 0 or cell [0] >= self.data.shape[0]
            or cell[1] < 0 or cell [1] >= self.data.shape[1]
        ):
            return False
        return True

    def findVisibleCells(self, position: Position, cellIndex: int) -> tuple[list, list]:
        match position:
            case Position.Top:
                startCell = (0, cellIndex)
                currentDirection = (Position.Top, Position.Bottom)
            case Position.Bottom:
                startCell = (self.data.shape[0] - 1, cellIndex)
                currentDirection = (Position.Bottom, Position.Top)
            case Position.Left:
                startCell = (cellIndex, 0)
                currentDirection = (Position.Left, Position.Right)
            case Position.Right:
                startCell = (cellIndex, self.data.shape[1] - 1)
                currentDirection = (Position.Right, Position.Left)
            case _:
                raise ValueError(f'Invalide position {position}')
        reflect = False
        headOnCells = []
        reflectionCells = []
        currentCell = startCell
        while self.isOnBoard(currentCell):
            if currentCell in self.data.mirrors.keys():
                reflect = True
                currentDirection = self.changeDirection[
                    (currentDirection, self.data.mirrors[currentCell])
                ]
            else:
                if reflect:
                    reflectionCells.append(currentCell)
                else:
                    headOnCells.append(currentCell)
            currentCell = (
                currentCell[0] + self.moveByDirection[currentDirection][0],
                currentCell[1] + self.moveByDirection[currentDirection][1]
            )
        return headOnCells, reflectionCells

    def getRenderedLinesInMainBoard(self) -> list[str]:
        renderedLines = []
        for row in range(self.data.shape[0]):
            renderUpRow = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
            renderRow = f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
            for col in range(self.data.shape[1]):
                if (row, col) in self.data.mirrors.keys():
                    if self.data.mirrors[(row, col)] == Mirror.LeftDownToRight:
                        renderRow += f' {Colors.BOLD}{Colors.BLUE}\{Colors.ENDC} '
                    elif self.data.mirrors[(row, col)] == Mirror.RightDownToLeft:
                        renderRow += f' {Colors.BOLD}{Colors.BLUE}/{Colors.ENDC} '
                    else:
                        raise ValueError(f'Invalid mirror {self.data.mirrors[(row, col)]}')
                else:
                    if self.vVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.RED}V{Colors.ENDC} '
                    elif self.gVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.YELLOW}G{Colors.ENDC} '
                    elif self.zVars[row][col].x == 1:
                        renderRow += f' {Colors.BOLD}{Colors.GREEN}Z{Colors.ENDC} '
                if col == self.data.shape[1] - 1:
                    renderRow += f'{Colors.BOLD}{Colors.PURPLE}|{Colors.ENDC}'
                    node = f'{Colors.BOLD}{Colors.PURPLE}+{Colors.ENDC}'
                else:
                    renderRow += f'{Colors.GRAY}|{Colors.ENDC}'
                    node = f'{Colors.GRAY}+{Colors.ENDC}'
                if row == 0:
                    renderUpRow += f'{Colors.BOLD}{Colors.PURPLE}---+{Colors.ENDC}'
                else:
                    renderUpRow += f'{Colors.GRAY}---{Colors.ENDC}{node}'
            renderedLines.append(renderUpRow)
            renderedLines.append(renderRow)
        renderedLines.append(
            f'{Colors.BOLD}{Colors.PURPLE}{"---".join(["+"] * (self.data.shape[1] + 1))}{Colors.ENDC}'
        )
        return renderedLines

    def visualize(self) -> None:
        super().visualize()
        renderedLinesInMainBoard = self.getRenderedLinesInMainBoard()
        topLine = f'{Colors.GRAY}    '
        for cell in self.data.visibility[Position.Top]:
            topLine += str(cell).center(4)
        topLine += f'   {Colors.ENDC}'
        print(topLine)
        for i, l in enumerate(renderedLinesInMainBoard):
            if i % 2:
                leftNumber = str(self.data.visibility[Position.Left][int(i/2)]).center(3)
                rightNumber = str(self.data.visibility[Position.Right][int(i/2)]).center(3)
                print(f'{Colors.GRAY}{leftNumber}{Colors.ENDC}{l}{Colors.GRAY}{rightNumber}{Colors.ENDC}')
            else:
                print(f'   {l}    ')
        bottomLine = f'{Colors.GRAY}    '
        for cell in self.data.visibility[Position.Bottom]:
            bottomLine += str(cell).center(4)
        bottomLine += f'   {Colors.ENDC}'
        print(bottomLine)
        return None
