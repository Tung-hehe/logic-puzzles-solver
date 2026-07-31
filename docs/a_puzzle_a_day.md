# A Puzzle A Day Model

## 1. Rules
1. The board is an irregular $7 \times 7$ grid: $6$ cells in the top-right and bottom-right corners are permanently blocked off, leaving a month area (Jan-Dec) and a day area (1-31).
2. Cover every remaining cell except the one matching the requested month and the one matching the requested day, using each of the $8$ pieces exactly once.
3. Pieces may be freely rotated and flipped.

## 2. Parameters
- $I = \{(0, 6), (1, 6), (6, 3), (6, 4), (6, 5), (6, 6)\}$: permanently blocked cells
- $B = \{(i, j) : 0 \leq i, j < 7\} \setminus I$: playable board cells
- $d$: requested day, $1 \leq d \leq 31$, with cell $day(d) = \left(2 + \left\lfloor \dfrac{d - 1}{7} \right\rfloor,\ (d - 1) \bmod 7\right)$
- $m$: requested month, $1 \leq m \leq 12$, with cell $month(m) = \left(\left\lfloor \dfrac{m - 1}{6} \right\rfloor,\ (m - 1) \bmod 6\right)$
- $P$: set of the $8$ pieces, each a fixed polyomino of $5$ or $6$ cells
- $K_p$: set of placements of piece $p \in P$ (every rotation and reflection, translated to every position) such that all of its cells stay inside $B$
- $C(p, k) \subseteq B$: cells covered by placement $k \in K_p$ of piece $p$

## 3. Variables
$$x(p, k) = \begin{cases}
    1 & \text{if piece } p \text{ is placed using placement } k \\
    0 & \text{otherwise}
\end{cases}, \forall p \in P, k \in K_p$$

## 4. Constraints

### 4.1. Each piece is used exactly once
$$
    \sum\limits_{k \in K_p}{x(p, k)} = 1, \forall p \in P
$$

### 4.2. Each board cell is covered exactly once, except the day and month cells
$$
    \sum\limits_{p \in P}{\sum\limits_{k \in K_p : (i, j) \in C(p, k)}{x(p, k)}} =
    \begin{cases}
        0 & \text{if } (i, j) \in \{day(d), month(m)\} \\
        1 & \text{otherwise}
    \end{cases}, \forall (i, j) \in B
$$
