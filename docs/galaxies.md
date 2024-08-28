# Galaxies Model
## 1. Rules
- Connect the dots to make edges so that each circle is surrounded by a symmetrical galaxy shape,
- The puzzle is completely tiled with galaxies.
- Each galaxy shape must be rotationally symmetric, having an identical appearance when rotated 180 degrees.

## 2. Parameters
- $n_R$: number of rows
- $n_C$: number of columns
- $n_G$: number of galaxies
- $C_g$: cell surround center of galaxy $g$
- $F_g$: set of all candidate cells of galaxy $g$ (all cells can be contained in galaxy $g$, according to limits and symmetry)
- $P(i, j, g)$: set of all path from cell $i, j$ to center of galaxy $g$
    - Each cell conect with 4 other cells: top, right, left, down
    - For each cell $(i, j) \in F_g$ we find all path from $c$ to the center of galaxy $g$
    - Remove paths containt at least one cycle
- $V(p)$: set of all cells in path $p$ except head cell and tail cell
- $s_r(i, j, g)$: symmetric row of cell $(i, j)$ with center of galaxy $g$
- $s_c(i, j, g)$: symmetric columns of cell $(i, j)$ with center of galaxy $g$

## 3. Variables
$$
x(i, j, g) = \begin{cases}
    1 & \text{if galaxy } g \text{containts cell } (i, j) \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i < n_R, 0 \leq j < n_C, 0 \leq g < n_G
$$

$$
    t(i, j, g, p) = \begin{cases}
    1 & x(u, v, g) = 1, \forall (u, v) \in V(p) \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq g < n_G, (i, j) in F_g, p \in P(i, j, g)
$$

## 4. Constraints

### 4.1. The puzzle is completely tiled with galaxies
$$ \sum_{g = 0}^{n_G - 1}{x(i, j, g)} = 1, \forall 0 \leq i < n_C, 0 \leq j < n_R, 0 \leq g < n_G$$

### 4.2. Galaxy containts its center.
$$x(i, j, g) = 1, \forall 0 \leq g < n_G, (i, j) \in C_g$$

### 4.3. Galaxy not containt the cell not in its candicate cells
$$x(i, j, g) = 0, \forall 0 \leq g < n_G, (i, j) \notin F_g$$

### 4.4. Symmetric cell.
$$x(i, j, g) = x(s_r(i, j, g), s_c(i, j, g), g), \forall 0 \leq g < n_G, (i, j) \in F_g$$

### 4.5. Represent $t$
$$
\begin{cases}
    \sum\limits_{(u, v) \in V(p)}{x(u, v)} \geq |V(p)| \cdot t(i, j, g, p) \\
    \sum\limits_{(u, v) \in V(p)}{x(u, v)} + 1\leq t(i, j, g, p) + |V(p)|\\
\end{cases}, \forall 0 \leq g < n_G, (i, j) \in F_g, p \in P(i, j, g)
$$

### 4.6. All cells of a galaxy are connected.
$$x(i, j, g) \leq \sum\limits_{p \in P(i, j, g)}{t(i, j, g, p)}, \forall 0 \leq g < n_G, (i, j) \in F_g$$
