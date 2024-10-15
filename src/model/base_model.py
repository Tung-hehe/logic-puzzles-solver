from datetime import datetime
from pathlib import Path

import mip

from src.utils import (
    DataIO,
    DataModel,
    Colors
)


class BaseModel:

    def __init__(self, dataPath: Path) -> None:
        self.start_time = datetime.now()
        self.data = DataModel(**DataIO.read_json_data(dataPath))
        self.verify_data()
        # Init model
        self._model = mip.Model(solver_name='CBC')
        # Set MIPFocus = 1
        self._model.solver.set_emphasis(mip.SearchEmphasis.FEASIBILITY)
        self._model.verbose = 0
        return None

    def verify_data(self) -> None:
        return None

    def init_model(self) -> None:
        self.add_variables()
        self.add_constraints()
        self.set_objective()
        return None

    def add_variable(self, vtype: str, name: str = '') -> mip.Var:
        return self._model.add_var(name=name, var_type=vtype)

    def add_variables(self) -> None:
        return None

    def add_constraint(self, constraint: mip.LinExpr, name: str = '') -> mip.Constr:
        return self._model.add_constr(constraint, name=name)

    def add_constraints(self) -> None:
        return None

    def set_objective(self) -> None:
        self._model.objective = mip.minimize(mip.LinExpr())
        return None

    def raise_error_infeasible(self) -> None:
        raise ValueError("Your puzzle is infeasible. Please check the data! Maybe you typed it wrong")

    def calculate_solving_time(self) -> None:
        self.solving_time = round((datetime.now() - self.start_time).total_seconds(), 2)
        return None

    def solve(self) -> None:
        self._model.optimize()
        if self._model.status != mip.OptimizationStatus.OPTIMAL:
            self.raise_error_infeasible()
        self.calculate_solving_time()
        return None

    def visualize(self) -> None:
        print(f'{Colors.BOLD}{Colors.GREEN}Done! Solving time: {self.solving_time}s{Colors.ENDC}')
        return None
