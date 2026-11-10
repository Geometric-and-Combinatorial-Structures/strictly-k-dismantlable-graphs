"""Reduced homology of clique complexes over F_2, including degree -1."""
from itertools import combinations
from .graphs import require


def faces(g):
    result = {-1: [()]}
    for size in range(1, len(g) + 1):
        level = [c for c in combinations(range(len(g)), size)
                 if all(g[u] >> v & 1 for u, v in combinations(c, 2))]
        if not level:
            break
        result[size - 1] = level
    return result


def rank(columns):
    pivots = {}
    for x in columns:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def rank_by_rows(columns, nrows):
    """Independent binary row elimination, used in the finite controls."""
    rows = [[(c >> i) & 1 for c in columns] for i in range(nrows)]
    r = 0
    for col in range(len(columns)):
        pivot = next((i for i in range(r, nrows) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(r + 1, nrows):
            if rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def betti(g, independent=False):
    fs = faces(g)
    ranks, boundaries = {-1: 0}, {}
    for degree in range(0, max(fs) + 1):
        row = {f: i for i, f in enumerate(fs[degree - 1])}
        columns = [sum(1 << row[f[:j] + f[j + 1:]] for j in range(len(f))) for f in fs[degree]]
        boundaries[degree] = columns
        ranks[degree] = rank(columns)
        if independent:
            require(ranks[degree] == rank_by_rows(columns, len(row)), 'Boundary ranks disagree')
        if degree > 0:
            for column in columns:
                composed = 0
                for i, image in enumerate(boundaries[degree - 1]):
                    if column >> i & 1:
                        composed ^= image
                require(composed == 0, 'Boundary does not square to zero')
    return {d: b for d in fs if (b := len(fs[d]) - ranks.get(d, 0) - ranks.get(d + 1, 0))}
