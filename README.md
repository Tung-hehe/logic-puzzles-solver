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
    "shape": 10, // size of puzzle
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
1. [./data/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_1.json): `#1` in [Star Battle 8x8, volume 1, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_8x8_v1_b1.pdf)
2. [./data/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_2.json): `#1` in [Star Battle 10x10, volume 1, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_10x10_v1_b1.pdf)
3. [./data/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_3.json): `#1` in [Star Battle 14x14, volume 1, book 1](https://files.krazydad.com/starbattle/sfiles/STAR_14x14_v1_b1.pdf)

Detail and puzzles: [Krazydad](https://krazydad.com/starbattle/)

## Binox
Rules:
1. The finished puzzle should be filled with Xs and Os.
2. Horizontally and vertically, there should never be a continuous run of the same symbol longer than 2.
3. There are an equal number of Xs and Os in each row and column.
4. All rows are unique. All columns are unique, too.

Data structure:
```json
    {
        "shape": 6, // size of puzzle
        "nSymbols": 2, // max number of the same symbol touching in each row, col
        "fixed": [ // fixed cells
            {"row": 0, "col": 0, "val": "X"}, // a fixed cells
            {"row": 1, "col": 2, "val": "O"},
            {"row": 2, "col": 1, "val": "O"},
            {"row": 2, "col": 2, "val": "O"},
            {"row": 3, "col": 0, "val": "X"},
            {"row": 3, "col": 5, "val": "X"},
            {"row": 4, "col": 2, "val": "O"},
            {"row": 4, "col": 5, "val": "X"}
        ]
    }
```

Example data:
1. [./data/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_1.json): `#1` in [Toughest 6x6 Binox, volume 1, book 1](https://files.krazydad.com/binox/sfiles/BINOX_6x6_TF_v1_4pp_b1.pdf)
2. [./data/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_2.json): `#1` in [Toughest 8x8 Binox, volume 1, book 1](https://files.krazydad.com/binox/sfiles/BINOX_8x8_TF_v1_4pp_b1.pdf)
3. [./data/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_3.json): `#1` in [Toughest 10x10 Binox, volume 1, book 1](https://files.krazydad.com/binox/sfiles/BINOX_10x10_TF_v1_4pp_b1.pdf)
4. [./data/puzzle_4.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_4.json): `#1` in [Toughest 12x12 Binox, volume 1, book 1](https://files.krazydad.com/binox/sfiles/BINOX_12x12_TF_v1_2pp_b1.pdf)
5. [./data/puzzle_5.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_5.json): `#1` in [Toughest 14x14 Binox, volume 1, book 1](https://files.krazydad.com/binox/sfiles/BINOX_14x14_TF_v1_2pp_b1.pdf)

Detail and puzzles: [Krazydad](https://krazydad.com/binox/)

## Troix
Rules:
1. The puzzle is filled with Xs, Os, and Is.
2. Horizontally and vertically, there can be no more than 2 of the same symbol touching (no three-in-a-row).
3. There is an equal number of each symbol in each row and column.

Detail and puzzles: [Krazydad](https://krazydad.com/troix/)
