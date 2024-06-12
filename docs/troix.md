# Troix Model

## 1. Rules
- The puzzle is filled with Xs, Os, and Is.
- Horizontally and vertically, there can be no more than 2 of the same symbol touching (no three-in-a-row).
- There is an equal number of each symbol in each row and column.


## 2. Parameters
- $n_R$: number of rows
- $n_C$: number of columns
- $F_X$: set of `X` fixed cells
- $F_O$: set of `O` fixed cells
- $F_I$: set of `I` fixed cells

## 3. Variables
$$x(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts X } \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

$$y(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts O } \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

$$z(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts I } \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

## 4. Constraints

### 4.1. Fixed cells
$$
\begin{cases}
    x(i, j) = 1, \forall (i, j) \in F_X \\
    y(i, j) = 1, \forall (i, j) \in F_O \\
    z(i, j) = 1, \forall (i, j) \in F_I
\end{cases}
$$
### 4.2. The puzzle is filled with Xs, Os, and Is.
$$x(i, j) + y(i, j) + z(i, j) == 1, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

### 4.3. There should never be a continuous run of the same symbol longer than 2 in each row.
$$
\begin{cases}
    x(i, j) + x(i, j + 1) + x(i, j + 2) \leq 2 \\
    y(i, j) + y(i, j + 1) + y(i, j + 2) \leq 2 \\
    z(i, j) + z(i, j + 1) + z(i, j + 2) \leq 2 \\
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C - 2
$$

### 4.4. There should never be a continuous run of the same symbol longer than 2 in each column.
$$
\begin{cases}
    x(i, j) + x(i + 1, j) + x(i + 2, j) \leq 2 \\
    y(i, j) + y(i + 1, j) + y(i + 2, j) \leq 2 \\
    z(i, j) + z(i + 1, j) + z(i + 2, j) \leq 2 \\
\end{cases}, \forall 0 \leq i \le n_R - 2, 0 \leq j \le n_C
$$

### 4.5. There are an equal number of Xs, Os and Is in each row.
$$
\begin{cases}
    \sum\limits_{j = 0}^{n_C - 1}{x(i, j)} = {n_C \over 3} \\
    \sum\limits_{j = 0}^{n_C - 1}{y(i, j)} = {n_C \over 3} \\
    \sum\limits_{j = 0}^{n_C - 1}{z(i, j)} = {n_C \over 3} \\
\end{cases}, \forall 0 \leq i \le n_R
$$

### 4.6. There are an equal number of Xs, Os and Is in each col.
$$
\begin{cases}
    \sum\limits_{i = 0}^{n_R - 1}{x(i, j)} = {n_R \over 3} \\
    \sum\limits_{i = 0}^{n_R - 1}{y(i, j)} = {n_R \over 3} \\
    \sum\limits_{i = 0}^{n_R - 1}{z(i, j)} = {n_R \over 3} \\
\end{cases}, \forall 0 \leq j \le n_C
$$
