import importlib
import sys
from rich.console import Console

from pathlib import Path


class PythonPath():
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path.remove(self.path)

with PythonPath(Path(__file__).absolute().parents[2]):
    puzzleName = sys.argv[1]
    dataPath = Path(sys.argv[2])
    puzzle = importlib.import_module(f'src.puzzles')
    model = getattr(puzzle, puzzleName)(dataPath)
    console = Console()
    with console.status("[bold green] Solving...") as status:
        model.solve()
    model.visualize()
