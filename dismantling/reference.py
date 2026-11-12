"""A separate set-based implementation of the finite decision procedure.

This module does not import the bit-mask recursion in graphs.py. It computes
the clique sum by listing cliques and decides membership on frozensets of
vertices. It is used to cross-check every unordered eleven-vertex extension.
"""
from functools import lru_cache


def classify(rows):
    neighbours = {v:frozenset(u for u in range(len(rows)) if rows[v] >> u & 1)
                  for v in range(len(rows))}

    def clique_sum(available):
        total = 1
        remaining = set(available)
        for v in sorted(available):
            remaining.remove(v)
            total -= clique_sum(remaining & neighbours[v])
        return total

    value = clique_sum(neighbours)
    if value != 0:
        return 'nonzero_q', value

    @lru_cache(None)
    def belongs(alive, level):
        if not alive:
            return False
        if any(alive - {v} <= neighbours[v] for v in alive):
            return True
        if level < 0:
            return False
        for v in sorted(alive, reverse=True):
            if belongs(alive & neighbours[v], level-1) and belongs(alive-{v}, level):
                return True
        return False

    alive = frozenset(neighbours)
    if belongs(alive,0):
        return 'D0', value
    if belongs(alive,1):
        return 'strict1', value
    if belongs(alive,2):
        return 'strict2', value
    return 'zero_q_outside_D2', value
