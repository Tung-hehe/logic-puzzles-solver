import itertools
import threading
import time
import sys

from pathlib import Path

import mip

from src.utils import PuzzleName, DataIO


class Model:

    def __init__(self, dataPath: Path, puzzleName: PuzzleName) -> None:
        self.data = DataIO.readJsonData(dataPath)
        # Init model
        self._model = mip.Model(name=puzzleName.value, solver_name='CBC')
        # Set MIPFocus = 1
        self._model.solver.set_emphasis(mip.SearchEmphasis.FEASIBILITY)
        self._model.verbose = 0
        self.initModel()
        return None

    def initModel(self) -> None:
        self.addVariables()
        self.addContraints()
        self.setObjective()
        return None

    def addVariable(self, vtype: str, name: str = '') -> mip.Var:
        return self._model.add_var(name=name, var_type=vtype)

    def addVariables(self) -> None:
        return None

    def addConstraint(self, constraint: mip.LinExpr, name: str = '') -> mip.Constr:
        return self._model.add_constr(constraint, name=name)

    def addContraints(self) -> None:
        return None

    def setObjective(self) -> None:
        self._model.objective = mip.minimize(mip.LinExpr())
        return None

    def solve(self) -> None:
        self._model.optimize()
        return None

    def visualize(self) -> None:
        assert self._model.status == mip.OptimizationStatus.OPTIMAL
        return None
