# Galaxies Model
## 1. Rules
- Connect horizontally or vertically adjacent dots to form a meandering path that forms a single loop, without crossing itself, or branching.
- The numbers indicate how many lines surround each cell.
- Empty cells may be surrounded by any number of lines (from 0 to 3).

## 2. Parameters
- $n_R$: number of rows
- $n_C$: number of columns
- $F$: set of all cells that must be surround of lines
- $L(i, j)$: number of lines must surround cell $(i, j)$
- $N(i, j)$: set of all lines connect to point $(i, j)$

## 3. Variables
$$
h(i, j) = \begin{cases}
    1 & \text{if vertical line } (i, j) \text{ is connected} \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i \le n_R + 1, 0 \leq j \le n_C
$$

$$
v(i, j) = \begin{cases}
    1 & \text{if vertical line } (i, j) \text{ is connected} \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i \le n_R, 0 \leq j \le n_C + 1
$$

$$
p(i, j) = \begin{cases}
    1 & \text{if point } (i, j) \text{ is connected} \\
    0 & \text{otherwise }
\end{cases}, \forall 0 \leq i \le n_R + 1, 0 \leq j \le n_C + 1
$$

## 4. Constraints

### 4.1. The numbers indicate how many lines surround each cell
$$ h(i, j) + h(i + 1, j) + v(i, j) + v(i, j + 1) = L(i, j) \forall (i, j) \in F$$

### 4.2. Lines connected into a number of disjoint closed cycles.
$$\sum\limits_{(u, v) \in N(i, j)} = 2 \cdot p(i, j) 0 \leq i \le n_R + 1, 0 \leq j \le n_C + 1$$

## 5. Implement

### 5.1. Break cycle constraint
- $H_c$: all horizontal lines in cycle $c$
- $V_c$: all vertical lines in cycle $c$

$$
\sum\limits_{(i, j) \in H_c} h(i, j) + \sum\limits_{(i, j) \in V_c} v(i, j) \leq 1
$$


### 5.2. Implement
```
BEGIN Slitherlink
    initalize model M;
    solve M;
    S := solution of M;
    WHILE (S have more than 1 cycle)
        add constraints to break all cycle in S;
        solve M;
        S := solution of M;
    END
    Return S;
END
```
