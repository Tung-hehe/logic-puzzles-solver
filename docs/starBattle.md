# Start Battle Model

## 1. Rules
- Each puzzle is divided into $s$ different regions.
- Each cage, row and column contains $n$ (base on $s$) star.
- The stars may not be adjacent to each other (not even diagonally).

## 2. Parameters
- $S$: set of cages
- $C_s$: cell of cage $s \in S$
- $n_R$: number of rows
- $n_C$: number of columns
- $n$: number of star each row, column and cage
- $N(i, j)$: set of neighboring cells of cell $(i, j)$
- $f(i, j)$: number of neighboring cells of cell $(i, j)$

## 3. Variables
$$x(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts a star } \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

## 4. Constraints

### 4.1. Each row contains $n$ stars
$$\sum\limits_{j = 0}^{n_C - 1}{x(i, j)} = n, \forall 0 \leq i \le n_R$$

### 4.2. Each column contains $n$ stars
$$\sum\limits_{i = 0}^{n_R - 1}{x(i, j)} = n, \forall 0 \leq j \le n_C$$

### 4.3. Each cage contains $n$ stars
$$\sum\limits_{\forall (i, j) \in C_s}{x(i, j)} = n, \forall s \in S$$

### 4.4 The stars may not be adjacent to each other (not even diagonally).
$$f(i, j) \cdot x(i, j) + \sum\limits_{\forall (p, q) \in N(i, j)}{x(p, q)} \leq f(i, j), \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$
