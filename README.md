# Logic puzzles solver

## Install libraries

```
pip install -r requirements.txt
```

## Run

- Change directory to this folder
- PuzzleName includes: `StarBattle`, ...
- Example for problem-data in `./data/`

```
python .\app\main.py [PuzzleName] [path/to/problem-data]
```

**Note**: *If you want to solve a new puzzle, you need to model this puzzle follow belowed data structure.*

## Star Battle
Rules:

    1. Each puzzle is divided into s different regions.
    2. Each cage, row and column contains n (base on s) star.
    3. The stars may not be adjacent to each other (not even diagonally).

Data structure:

    ```json
    {
        "shape": 10, // shape of puzzle
        "nStars": 2, // nStar each row, col, cage
        "cages": [
            // a cage includes cells
            [
                {"row": 0, "col": 0}, // a cell in cage
                {"row": 0, "col": 1},
                {"row": 0, "col": 2},
                {"row": 0, "col": 3},
                {"row": 1, "col": 0}
            ],
            // other cage
            [
                {"row": 0, "col": 4},
                {"row": 0, "col": 5},
                {"row": 0, "col": 6},
                {"row": 0, "col": 7},
                {"row": 0, "col": 8}
            ]
            // ...
        ]
    }
    ```

Example data:
1. [./data/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_1.json): `#1` in [star battle 8x8, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_8x8_v1_b1.pdf)
2. [./data/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_2.json): `#1` in [star battle 10x10, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_10x10_v1_b1.pdf)
3. [./data/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_3.json): `#1` in [star battle 14x14, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_14x14_v1_b1.pdf)

Detail and puzzles: [Krazydad](https://krazydad.com/starbattle/)

## Troix

1. The puzzle is filled with Xs, Os, and Is.
2. Horizontally and vertically, there can be no more than 2 of the same symbol touching (no three-in-a-row).
3. There is an equal number of each symbol in each row and column.

Detail and puzzles: [Krazydad](https://krazydad.com/troix/)
