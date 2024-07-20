# Sudoku Model

## 1. Rules
Rules:
1. Each row, column, block not contain duplicate values
2. Value in cell in range [1, $n$]

## 2. Parameters
- $n$: size of grid
- $F$: set of fixed cells
- $V(i, j)$: value of fixed cell $(i, j)$
- $B_b$: set of cells in a block with order $b$, $0 \leq b < \sqrt{n}$

## 3. Variables
$$x(i, j, k) = \begin{cases}
    1 & \text{if cell } (i, j)\text{ contain } {k} \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i, j < n, 0 < k \leq n$$

## 4. Constraints

### 4.1. Fixed cells
$$
    x(i, j, V(i, j)) = 1, \forall (i, j) \in F
$$

### 4.2. Each cell contain one value.
$$
    \sum\limits_{k = 1}^{n}{x(i, j, k)} \leq 1, \forall 0 \leq i, j < n
$$

### 4.3. Each row not contain duplicate values.
$$
    \sum\limits_{j = 0}^{n - 1}{x(i, j, k)} = 1, \forall 0 \leq i  < n, 1 \leq k  \leq n
$$

### 4.4. Each column not contain duplicate values.
$$
    \sum\limits_{i = 0}^{n - 1}{x(i, j, k)} = 1, \forall 0 \leq j < n, 1 \leq k  \leq n
$$

### 4.5. Each column not contain duplicate values.
$$
    \sum\limits_{(i, j) \in B_b}{x(i, j, k)} = 1, \forall 0 \leq b < \sqrt{n}, 1 \leq k  \leq n
$$
