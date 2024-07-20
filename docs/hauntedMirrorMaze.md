# Haunted Mirror Maze Model
## 1. Rules
- Fill each empty box of the puzzle grid with the right monster: a ghost, vampire, or zombie
- The clues along the edges tell you how many monsters you can see from that point looking into the grid, and the diagonal lines are mirrors that reflect a line of sight 90 degrees, as with a laser..
- Vampires (V) are seen only head-on (have no reflection in a mirror).
- Ghosts (G) are only seen as reflections in mirrors (not head-on).
- Zmobies (Z) are always seen.
- Each puzzle also has a handy list of monsters so you know how many of each type are hiding in that mirror maze.
- Some cells contain the same monsters.
- Some cells contain fixed monsters.

## 2. Parameters
- $n_R$: number of rows
- $n_C$: number of columns
- $V(i, j)$: number of monster can see from cell $(i, j)$
- $H(i, j)$: number cell can be seen head-on from cell $(i, j)$
- $R(i, j)$: number cell can be seen as reflections in mirrors from cell $(i, j)$
- $M$: set of cells contain mirrors
- $n_V$: number of vampires
- $n_G$: number of ghosts
- $n_Z$: number of zombies
- $S$: set of cells contain the same monsters
- $F_V$: set of cells contain fixed vampires
- $F_G$: set of cells contain fixed ghosts
- $F_Z$: set of cells contain fixed Zombies

## 3. Variables
$$v(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts a vampire } \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i < n_R, 0 \leq j < n_C$$

$$g(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts a ghost } \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i < n_R, 0 \leq j < n_C$$

$$z(i, j) = \begin{cases}
    1 & \text{if cell } (i, j) \text{ containts a zombie } \\
    0 & \text{otherwise}
\end{cases}, \forall 0 \leq i < n_R, 0 \leq j < n_C$$

## 4. Constraints
### 4.1. Mirror cell not contain monster
$$
\begin{cases}
    v(i, j) = 0 \\
    g(i, j) = 0 \\
    z(i, j) = 0\\
\end{cases}, \forall (i, j) \in M
$$

### 4.2. Each cell containt one monster except mirror cells
$$v(i, j) + g(i, j) + z(i, j) == 1, \forall 0 \leq i < n_R, 0 \leq j < n_C, (i, j) \notin M$$

### 4.3. Fixed cells
$$
\begin{cases}
    v(i, j) = 0, \forall (i, j) \in F_V \\
    g(i, j) = 0, \forall (i, j) \in F_G \\
    z(i, j) = 0, \forall (i, j) \in F_Z \\
\end{cases}
$$

### 4.3. Same cells
$$
\begin{cases}
    v(i, j) = v(x, y) \\
    g(i, j) = g(x, y) \\
    z(i, j) = z(x, y) \\
\end{cases}, \forall (i, j), (x, y) \in S
$$

### 4.4. Fix number of monsters
$$
\begin{cases}
    \sum\limits_{i = 0}^{n_R - 1}\sum\limits_{j = 0}^{n_C - 1}{v(i, j)} = n_V \\
    \sum\limits_{i = 0}^{n_R - 1}\sum\limits_{j = 0}^{n_C - 1}{g(i, j)} = n_G \\
    \sum\limits_{i = 0}^{n_R - 1}\sum\limits_{j = 0}^{n_C - 1}{Z(i, j)} = n_Z \\
\end{cases}, \forall (i, j), (x, y) \in S
$$

### 4.5. Visible monsters from top
$$
    \sum\limits_{(x, y) \in H(0, j)}{v(x, y)}
    + \sum\limits_{(x, y) \in R(0, j)}{g(x, y)}
    + \sum\limits_{(x, y) \in H(0, j) \cup R(0, j)}{z(x, y)}
    = V(0, j), \forall 0 \leq j \leq n_C
$$

### 4.6. Visible monsters from bottom
$$
    \sum\limits_{(x, y) \in H(|n_R| - 1, j)}{v(x, y)}
    + \sum\limits_{(x, y) \in R(|n_R| - 1, j)}{g(x, y)}
    + \sum\limits_{(x, y) \in H(|n_R| - 1, j) \cup R(|n_R| - 1, j)}{z(x, y)}
    = V(|n_R| - 1, j), \forall 0 \leq j \leq n_C
$$

### 4.7. Visible monsters from left
$$
    \sum\limits_{(x, y) \in H(i, 0)}{v(x, y)}
    + \sum\limits_{(x, y) \in R(i, 0)}{g(x, y)}
    + \sum\limits_{(x, y) \in H(i, 0) \cup R(i, 0)}{z(x, y)}
    = V(i, 0), \forall 0 \leq i \leq n_R
$$

### 4.8. Visible monsters from right
$$
    \sum\limits_{(x, y) \in H(i, |n_R| - 1)}{v(x, y)}
    + \sum\limits_{(x, y) \in R(i, |n_R| - 1)}{g(x, y)}
    + \sum\limits_{(x, y) \in H(i, |n_R| - 1) \cup R(i, |n_R| - 1)}{z(x, y)}
    = V(i, |n_R| - 1), \forall 0 \leq i \leq n_R
$$
