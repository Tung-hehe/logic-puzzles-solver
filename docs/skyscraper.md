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

For every sight line $L$, interior position $1 \leq p \leq n - 2$ and height $p \leq k \leq n - 2$:
$$z_L(p, k) = \begin{cases}
    1 & \text{if the building at } L_p \text{ has height } k + 1 \text{ and is strictly taller than every building at } L_0, \ldots, L_{p-1} \\
    0 & \text{otherwise}
\end{cases}$$

($p \leq k$ because a building visible from behind $p$ closer buildings needs at least $p$ smaller heights before it; $k \leq n - 2$ because the tallest building, height $n$, is handled separately below since it is always visible.)

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
For every sight line $L \in \mathcal{L}$, $1 \leq p \leq n - 2$, $p \leq k \leq n - 2$, let

$$
    taller\_before(L, p, k) = \sum\limits_{q = 0}^{p - 1}{\sum\limits_{k' = k + 1}^{n - 1}{x(r_q, c_q, k')}}
$$

be the number of buildings standing between the viewer and position $p$ that are taller than $k + 1$. Then $z_L(p, k)$ is pinned to "cell $L_p$ has height $k + 1$ and nothing taller stands in front of it" by:
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
    \sum\limits_{p = 1}^{n - 2}{\sum\limits_{k = p}^{n - 2}{z_L(p, k)}} + \sum\limits_{p = 0}^{n - 1}{x(r_p, c_p, n - 1)} \geq v(L) - 1, \forall L \in \mathcal{L}
$$

The second sum is exactly $1$ (the tallest building, height $n$, occurs once on $L$ and is always visible from both ends). The first cell $L_0$ is likewise always visible but is only picked up explicitly by that same term when it happens to hold height $n$; otherwise its guaranteed visibility is absorbed by the $-1$ slack on the right-hand side, which is why the constraint is an inequality rather than an equality.
