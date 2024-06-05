import argparse
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

def main():
    parser = argparse.ArgumentParser(
        description="Solve a puzzle",
        epilog='example: python .\\app\main.py -p StarBattle -d ./data/star-battle/puzzle_1.json',
        usage='python .\\app\main.py -p [P] -d [D]'
    )
    parser.add_argument('-p', type=str, nargs='?', help='puzzle name, include: StarBattle, Binox, Galaxies')
    parser.add_argument('-d', type=str, nargs='?', help='path to data of problem')
    opt = parser.parse_args()
    with PythonPath(Path(__file__).absolute().parents[2]):
        puzzle = importlib.import_module(f'src.puzzles')
        model = getattr(puzzle, opt.p)(Path(opt.d))
        console = Console()
        with console.status("[bold green] Solving...") as status:
            model.initModel()
            model.solve()
        model.visualize()

if __name__ == '__main__':
    main()
