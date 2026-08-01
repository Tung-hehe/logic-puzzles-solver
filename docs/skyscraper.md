# Skyscraper Model

## 1. Rules
1. Fill the grid with buildings of height $1$ to $n$, once each per row and per column (a Latin square).
2. Each clue placed outside the grid tells how many buildings are visible looking into that row/column from that side; a building is visible if it is taller than every building before it from that vantage point.

## 2. Parameters
- $n$: size of grid
- $F$: set of fixed cells
- $V(i, j)$: value of fixed cell $(i, j)$
- $\mathcal{L}$: set of sight lines. Each sight line $L \in \mathcal{L}$ is the ordered sequence of cells of one row (read left-to-right or right-to-left) or one column (read top-to-bottom or bottom-to-top), as seen by the viewer standing at one of the four clues. $L_p = (r_p, c_p)$ denotes the cell at position $p$ along $L$ ($0 \leq p < n$, $L_0$ closest to the viewer).
- $v(L)$: visible-building clue for sight line $L$

## 3. Variables
$$x(i, j, k) = \begin{cases}
    1 & \text{if cell } (i, j)\text{ has height } k + 1 \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i, j < n, 0 \leq k < n$$

For every sight line $L$, position $0 \leq p \leq n - 1$ and height $0 \leq k \leq n - 1$:
$$z_L(p, k) = \begin{cases}
    1 & \text{if the building at } L_p \text{ has height } k + 1 \text{ and is strictly taller than every building at } L_0, \ldots, L_{p-1} \\
    0 & \text{otherwise}
\end{cases}$$

(For $p = 0$ there is nothing standing before it, so $z_L(0, k)$ always equals $x(r_0, c_0, k)$: the first building is always visible, whatever its height.)

## 4. Constraints

### 4.1. Fixed cells
$$
    x(i, j, V(i, j)) = 1, \forall (i, j) \in F
$$

### 4.2. Each cell contains one height
$$
    \sum\limits_{k = 0}^{n - 1}{x(i, j, k)} = 1, \forall 0 \leq i, j < n
$$

### 4.3. Each row contains every height exactly once
$$
    \sum\limits_{j = 0}^{n - 1}{x(i, j, k)} = 1, \forall 0 \leq i < n, 0 \leq k < n
$$

### 4.4. Each column contains every height exactly once
$$
    \sum\limits_{i = 0}^{n - 1}{x(i, j, k)} = 1, \forall 0 \leq j < n, 0 \leq k < n
$$

### 4.5. Visible buildings per sight line
For every sight line $L \in \mathcal{L}$, $0 \leq p \leq n - 1$, $0 \leq k \leq n - 1$, let

$$
    taller\_before(L, p, k) = \sum\limits_{q = 0}^{p - 1}{\sum\limits_{k' = k + 1}^{n - 1}{x(r_q, c_q, k')}}
$$

be the number of buildings standing between the viewer and position $p$ that are taller than $k + 1$ (an empty sum, hence $0$, when $p = 0$). Then $z_L(p, k)$ is pinned to "cell $L_p$ has height $k + 1$ and nothing taller stands in front of it" by:
$$
    taller\_before(L, p, k) + p \cdot z_L(p, k) - p \leq 0
$$
$$
    x(r_p, c_p, k) - z_L(p, k) \geq 0
$$
$$
    x(r_p, c_p, k) - taller\_before(L, p, k) - z_L(p, k) \leq 0
$$

and the clue is enforced by
$$
    \sum\limits_{p = 0}^{n - 1}{\sum\limits_{k = 0}^{n - 1}{z_L(p, k)}} = v(L), \forall L \in \mathcal{L}
$$

Since every $(p, k)$ pair is covered, $z_L(p, k)$ exactly indicates whether the building at position $p$ is visible, so the sum above is exactly the true number of visible buildings on $L$ and the clue can be enforced with equality.

**A note on an earlier, buggy version of this constraint:** an earlier version of this model only defined $z_L$ for interior positions $1 \leq p \leq n - 2$ and heights $p \leq k \leq n - 2$, handled the tallest building (height $n$, always visible wherever it stands) through a separate term $\sum_{p} x(r_p, c_p, n - 1)$, and handled the always-visible first cell $L_0$ by relaxing the right-hand side to $v(L) - 1$ instead of $v(L)$. That inequality is unsound whenever the tallest building happens to stand at $L_0$: no other building on the line can then be a record (nothing can be taller than the tallest), so the left-hand side is always exactly $1$ regardless of the rest of the line, which lets the inequality hold for any clue $v(L) \leq 2$ even when the true visible count is $1$. Concretely, the puzzle in `data/skyscraper/puzzle_1.json` solves to a grid whose last row, read from the left, is `5 2 1 4 3` (only $1$ building visible); with the old formula, changing that row's `left` clue from `1` to `2` still solved to the exact same grid, silently accepting a clue the solution does not actually satisfy. The uniform formulation above (every position paired with every height, enforced with equality) has no such gap.
