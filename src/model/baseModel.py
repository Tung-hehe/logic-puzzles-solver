from datetime import datetime
from pathlib import Path

import mip

from src.utils import DataIO, Colors


class BaseModel:

    def __init__(self, dataPath: Path) -> None:
        self.startTime = datetime.now()
        self.data = DataIO.readJsonData(dataPath)
        # Init model
        self._model = mip.Model(solver_name='CBC')
        # Set MIPFocus = 1
        self._model.solver.set_emphasis(mip.SearchEmphasis.FEASIBILITY)
        self._model.verbose = 0
        return None

    def initModel(self) -> None:
        self.addVariables()
        self.addConstraints()
        self.setObjective()
        return None

    def addVariable(self, vtype: str, name: str = '') -> mip.Var:
        return self._model.add_var(name=name, var_type=vtype)

    def addVariables(self) -> None:
        return None

    def addConstraint(self, constraint: mip.LinExpr, name: str = '') -> mip.Constr:
        return self._model.add_constr(constraint, name=name)

    def addConstraints(self) -> None:
        return None

    def setObjective(self) -> None:
        self._model.objective = mip.minimize(mip.LinExpr())
        return None

    def raiseErrorInfeasible(self) -> None:
        raise ValueError("Your puzzle is infeasible. Please check the data! Maybe you typed it wrong")

    def calculateSolvingTime(self) -> None:
        self.solvingTime = round((datetime.now() - self.startTime).total_seconds(), 2)
        return None

    def solve(self) -> None:
        self._model.optimize()
        if self._model.status != mip.OptimizationStatus.OPTIMAL:
            self.raiseErrorInfeasible()
        self.calculateSolvingTime()
        return None

    def visualize(self) -> None:
        print(f'{Colors.BOLD}{Colors.GREEN}Done! Solving time: {self.solvingTime}s{Colors.ENDC}')
        return None
