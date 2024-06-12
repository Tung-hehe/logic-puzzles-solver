# Logic puzzles solver

## Install libraries

```
pip install -r requirements.txt
```

## Run
- Change directory to this folder and run
    ```
    python .\app\main.py -p [P] -d [D]
    ```
- `[P]` is a puzzle sorted name

    | Sorted name | Puzzle name    |
    | :---------: | :------------- |
    |     `B`     | Binox          |
    |     `G`     | Galaxies       |
    |     `SB`    | StarBattle     |
    |     `T`     | Troix          |
    |     `SL`    | Slitherlink    |

- `[D]` is path to problem data
- Example running
    ```
    python .\app\main.py -p SB -d ./data/star-battle/puzzle_1.json
    ```
- Help `-h` for more details:
    ```
    python .\app\main.py -h
    ```
- Example data in `./data/`

**Note**: *If you want to solve a new puzzle, you need to model this puzzle follow belowed data structure.*

## Star Battle
Rules:
1. Each puzzle is divided into $s$ different regions.
2. Each cage, row and column contains $n$ (base on $s$) star.
3. The stars may not be adjacent to each other (not even diagonally).

Data structure:
```json
{
    "shape": [10, 10], // size of puzzle [number of rows, number of columns]
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
1. [./data/star-battle/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_1.json): `#1` in [Star Battle 8x8, Volume 1, Book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_8x8_v1_b1.pdf)
2. [./data/star-battle/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_2.json): `#1` in [Star Battle 10x10, Volume 1, Book 1](https://files.krazydad.com/starbattle/sfiles/STAR_R2_10x10_v1_b1.pdf)
3. [./data/star-battle/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/star-battle/puzzle_3.json): `#1` in [Star Battle 14x14, Volume 1, Book 1](https://files.krazydad.com/starbattle/sfiles/STAR_14x14_v1_b1.pdf)

Modeling: [./docs/starBattle.md](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/docs/starBattle.md)

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
        "shape": [6, 6], // size of puzzle [number of rows, number of columns]
        "nSymbols": 2, // max number of the same symbol touching in each row, col
        "fixed": [ // fixed cells
            {"row": 0, "col": 0, "val": "X"}, // a fixed cell
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
1. [./data/binox/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_1.json): `#1` in [Toughest 6x6 Binox, Volume 1, Book 1](https://files.krazydad.com/binox/sfiles/BINOX_6x6_TF_v1_4pp_b1.pdf)
2. [./data/binox/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_2.json): `#1` in [Toughest 8x8 Binox, Volume 1, Book 1](https://files.krazydad.com/binox/sfiles/BINOX_8x8_TF_v1_4pp_b1.pdf)
3. [./data/binox/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_3.json): `#1` in [Toughest 10x10 Binox, Volume 1, Book 1](https://files.krazydad.com/binox/sfiles/BINOX_10x10_TF_v1_4pp_b1.pdf)
4. [./data/binox/puzzle_4.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_4.json): `#1` in [Toughest 12x12 Binox, Volume 1, Book 1](https://files.krazydad.com/binox/sfiles/BINOX_12x12_TF_v1_2pp_b1.pdf)
5. [./data/binox/puzzle_5.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/binox/puzzle_5.json): `#1` in [Toughest 14x14 Binox, Volume 1, Book 1](https://files.krazydad.com/binox/sfiles/BINOX_14x14_TF_v1_2pp_b1.pdf)

Modeling: [./docs/binox.md](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/docs/binox.md)

Detail and puzzles: [Krazydad](https://krazydad.com/binox/)

## Troix
Rules:
1. The puzzle is filled with Xs, Os, and Is.
2. Horizontally and vertically, there can be no more than 2 of the same symbol touching (no three-in-a-row).
3. There is an equal number of each symbol in each row and column.

Data structure:
```json
    {
        "shape": [9, 9], // size of puzzle [number of rows, number of columns]
        "nSymbols": 2, // max number of the same symbol touching in each row, col
        "fixed": [ // fixed cells
            {"row": 0, "col": 0, "val": "X"}, // a fixed cell
            {"row": 3, "col": 0, "val": "I"},
            {"row": 3, "col": 1, "val": "O"},
            {"row": 3, "col": 3, "val": "X"},
        ]
    }
```

Example data:
1. [./data/troix/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/troix/puzzle_1.json): `#1` in [9x9 TroixPuzzles, Volume 1, Book 1](https://files.krazydad.com/troix/sfiles/TROIX_9x9_regular_v1_4pp_b1.pdf)
2. [./data/troix/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/troix/puzzle_2.json): `#1` in [12x12 TroixPuzzles, Volume 1, Book 1](https://files.krazydad.com/troix/sfiles/TROIX_12x12_regular_v1_2pp_b1.pdf)
3. [./data/troix/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/troix/puzzle_3.json): `#1` in [15x15 TroixPuzzles, Volume 1, Book 1](https://files.krazydad.com/troix/sfiles/TROIX_15x15_regular_v1_2pp_b1.pdf)
4. [./data/troix/puzzle_4.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/troix/puzzle_3.json): `#1` in [21x21 TroixPuzzles, Volume 1, Book 1](https://files.krazydad.com/troix/sfiles/TROIX_21x21_regular_v1_1pp_b1.pdf)

Modeling: [./docs/troix.md](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/docs/troix.md)

Detail and puzzles: [Krazydad](https://krazydad.com/troix/)

## Galaxies
Rules:
1. Connect the dots to make edges so that each circle is surrounded by a symmetrical galaxy shape,
2. The puzzle is completely tiled with galaxies.
3. Each galaxy shape must be rotationally symmetric, having an identical appearance when rotated 180 degrees.

Data structure:
```json
    {
        "shape": [21, 11], // size of puzzle [number of rows, number of columns]
        "galaxies": [ // centers of galaxies
            [
                {"row": 0, "col": 4} // center of a galaxy
            ],
            [
                {"row": 0, "col": 0},
                {"row": 1, "col": 0}
            ],
            [
                {"row": 0, "col": 5},
                {"row": 0, "col": 6},
                {"row": 1, "col": 5},
                {"row": 1, "col": 6}
            ],
        ]
    }
```

Example data:
1. [./data/galaxies/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/galaxies/puzzle_1.json): `#16` in [ 7x7 Galaxy, Book 1](https://files.krazydad.com/galaxies/books/GAL_d7_b1.pdf)
2. [./data/galaxies/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/galaxies/puzzle_2.json): `#10` in [ 10x10 Galaxy, Book 1](https://files.krazydad.com/galaxies/books/GAL_d10_b1.pdf)
3. [./data/galaxies/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/galaxies/puzzle_3.json): `#5` in [ 21x11 Galaxy, Book 1](https://files.krazydad.com/galaxies/books/GAL_d11_b1.pdf)
4. [./data/galaxies/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/galaxies/puzzle_4.json): `#2` in [ 21x21 Galaxy, Book 1](https://files.krazydad.com/galaxies/books/GAL_d21_b1.pdf)

Modeling: [./docs/galaxies.md](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/docs/galaxies.md)

Detail and puzzles: [Krazydad](https://krazydad.com/galaxies/)

## Slitherlink
Rules:
1. Connect horizontally or vertically adjacent dots to form a meandering path that forms a single loop, without crossing itself, or branching.
2. The numbers indicate how many lines surround each cell. Empty cells may be surrounded by any number of lines (from 0 to 3).

Data structure:
```json
    {
        "shape": [7, 7], // size of puzzle [number of rows, number of columns]
        "nLinesSurround": [ // number of lines surround cells
            {"row": 0, "col": 0, "val": 2},
            {"row": 0, "col": 1, "val": 2},
        ]
    }
```

Example data:
1. [./data/slitherlink/puzzle_1.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/slitherlink/puzzle_1.json): `#1` in [ Tough Slitherlink Puzzles, 7 x 7 Format, Volume 1, Book 1](https://files.krazydad.com/slitherlink/sfiles/sl_d2_07x07_b001.pdf)
2. [./data/slitherlink/puzzle_2.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/slitherlink/puzzle_2.json): `#1` in [ Tough Slitherlink Puzzles, 10 x 10 Format, Volume 1, Book 1](https://files.krazydad.com/slitherlink/sfiles/sl_d2_10x10_b001.pdf)
3. [./data/slitherlink/puzzle_3.json](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/data/slitherlink/puzzle_3.json): `#1` in [ Tough Slitherlink Puzzles, 20 x 20 Format, Volume 1, Book 1](https://files.krazydad.com/slitherlink/sfiles/sl_d2_20x20_b001.pdf)

Modeling: [./docs/slitherlink.md](https://github.com/Tung-hehe/LogicPuzzlesSolver/blob/main/docs/slitherlink.md)

Detail and puzzles: [Krazydad](https://krazydad.com/slitherlink/)
