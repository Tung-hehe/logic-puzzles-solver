import argparse
import importlib
import sys
from rich.console import Console

from pathlib import Path


PUZZLE_NAME = {
    'B': 'Binox',
    'G': 'Galaxies',
    'S': 'Sudoku',
    'SB': 'StarBattle',
    'T': 'Troix',
    'SL': 'Slitherlink',
    'HMM': 'HauntedMirrorMaze',
    'APAD': 'APuzzleADay'
}

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
        epilog='example: python main.py -p StarBattle -d ./data/star_battle/puzzle_1.json',
        usage='python main.py -p [P] -d [D]'
    )
    parser.add_argument('-p', type=str, nargs='?', help='puzzle name')
    parser.add_argument('-d', type=str, nargs='?', help='path to data of problem, or day for puzzle "A puzzle a day" (example: "10-05")')
    parser.add_argument('-s', type=str, nargs='?', help='save solution path')
    opt = parser.parse_args()
    with PythonPath(Path(__file__).absolute().parents[2]):
        puzzle = importlib.import_module(f'src.puzzles')
        model = getattr(puzzle, PUZZLE_NAME[opt.p])(opt.d)
        console = Console()
        with console.status("[bold green] Solving...") as status:
            model.init_model()
            model.solve()
        model.visualize()
        if opt.s:
            model.export_solution(Path(opt.s))

if __name__ == '__main__':
    main()
