# Binox Model

## 1. Rules
- The finished puzzle should be filled with Xs and Os.
- Horizontally and vertically, there should never be a continuous run of the same symbol longer than 2.
- There are an equal number of Xs and Os in each row and column.
- All rows are unique. All columns are unique, too.

## 2. Parameters
- $n_R$: number of rows
- $n_C$: number of columns
- $F_X$: set of `X` fixed cells
- $F_O$: set of `O` fixed cells

## 3. Variables
$$x(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts X } \\
    0 & \text{if cell } (i, j) \text{ containts O }
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C$$

$$y(i, j, k) = \begin{cases}
    1 & \text{if } x(i, k) = x(j, k) \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i, j \le n_R, i\ne j, 0 \leq k \le n_C$$

$$z(i, j, k) = \begin{cases}
    1 & \text{if } x(k, i) = x(k, j) \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i, j \le n_C, i\ne j, 0 \leq k \le n_R$$

## 4. Constraints

### 4.1. Fixed cells
$$
\begin{cases}
    x(i, j) = 1, \forall (i, j) \in F_X\\
    x(i, j) = 0, \forall (i, j) \in F_O
\end{cases}
$$

### 4.2. There should never be a continuous run of the same symbol longer than 2 in each row.
$$
\begin{cases}
    x(i, j) + x(i, j + 1) + x(i, j + 2) \leq 2 \\
    x(i, j) + x(i, j + 1) + x(i, j + 2) \geq 1
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C - 2
$$

### 4.3. There should never be a continuous run of the same symbol longer than 2 in each column.
$$
\begin{cases}
    x(i, j) + x(i + 1, j) + x(i + 2, j) \leq 2 \\
    x(i, j) + x(i + 1, j) + x(i + 2, j) \geq 1
\end{cases}, \forall 0 \leq i \le n_R - 2, 0 \leq j \le n_C
$$

### 4.4. There are an equal number of Xs and Os in each row.
$$\sum\limits_{j = 0}^{n_C - 1}{x(i, j)} = {n_C \over 2}, \forall 0 \leq i \le n_R$$

### 4.5. There are an equal number of Xs and Os in each col.
$$\sum\limits_{i = 0}^{n_R - 1}{x(i, j)} = {n_R \over 2}, \forall 0 \leq j \le n_C$$

### 4.6. Represent $y$
$$
\begin{cases}
    y(i, j, k) + x(i, k) + x(j, k) \geq 1 \\
    y(i, j, k) + x(i, k) \leq x(j, k) + 1 \\
    y(i, j, k) + x(j, k) \leq x(i, k) + 1 \\
    x(i, k) + x(j, k) \leq y(i, j, k) + 1
\end{cases}, \forall 0 \leq i, j \le n_R, i \ne j, 0 \leq k \le n_C
$$

### 4.7. All rows are unique
$$\sum\limits_{k = 0}^{n_C - 1}{y(i, j, k)} \leq n_C - 1, \forall 0 \leq i, j \le n_R, i \ne j$$

### 4.8. Represent $z$
$$
\begin{cases}
    z(i, j, k) + x(k, i) + x(k, j) \geq 1 \\
    z(i, j, k) + x(k, i) \leq x(k, j) + 1 \\
    z(i, j, k) + x(k, j) \leq x(k, i) + 1 \\
    x(k, i) + x(k, j) \leq z(i, j, k) + 1
\end{cases}, \forall 0 \leq k \le n_R, 0 \leq i, j \le n_C, i \ne j
$$

### 4.9. All columns are unique
$$\sum\limits_{k = 0}^{n_R - 1}{z(i, j, k)} \leq n_R - 1, \forall 0 \leq i, j \le n_C, i \ne j$$
