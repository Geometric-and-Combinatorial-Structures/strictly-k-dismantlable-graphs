"""Finite simple graphs with integer labels 0,...,n-1.

An adjacency row is an integer whose set bits are the neighbours.
Only this module needs that representation; public files use vertex lists.
"""
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def validate(g):
    n = len(g)
    for v, row in enumerate(g):
        require(type(row) is int and 0 <= row < 1 << n, 'Invalid adjacency row')
        require(not row >> v & 1, 'A simple graph has no loops')
        require(all(g[u] >> v & 1 for u in vertices(row)), 'Adjacency is not symmetric')
    return tuple(g)


def from_lists(rows):
    n = len(rows)
    for row in rows:
        require(all(type(v) is int and 0 <= v < n for v in row), 'Invalid vertex label')
        require(len(row) == len(set(row)), 'Repeated neighbour')
    return validate(tuple(sum(1 << v for v in row) for row in rows))


def from_edges(n, edges):
    require(type(n) is int and n >= 0, 'Invalid graph order')
    g = [0] * n
    seen = set()
    for u, v in edges:
        require(type(u) is int and type(v) is int and 0 <= u < v < n, 'Invalid ordered edge')
        require((u, v) not in seen, 'Repeated edge')
        seen.add((u, v))
        g[u] |= 1 << v
        g[v] |= 1 << u
    return tuple(g)


def edges(g):
    return [(v, u) for v, row in enumerate(g) for u in vertices(row) if v < u]


def induced(g, subset):
    vs = list(subset)
    require(len(vs) == len(set(vs)) and all(type(v) is int and 0 <= v < len(g) for v in vs),
            'Invalid induced vertex set')
    return tuple(sum(1 << j for j, u in enumerate(vs) if g[v] >> u & 1) for v in vs)


def cone(g, mask=None):
    if mask is None:
        mask = (1 << len(g)) - 1
    return next((v for v in vertices(mask) if mask & ~(g[v] | (1 << v)) == 0), None)


def fold(g, mask, source, target):
    require(source != target and (mask >> source & 1) and (mask >> target & 1), 'Invalid fold vertices')
    require(((g[source] | (1 << source)) & mask) & ~(g[target] | (1 << target)) == 0,
            'Closed-neighbourhood inclusion fails')
    return mask ^ (1 << source)


def coefficients(g, mask=None):
    """Clique coefficients from C_G=C_(G-v)+z C_(N(v))."""
    if mask is None:
        mask = (1 << len(g)) - 1

    @lru_cache(None)
    def rec(m):
        if not m:
            return (1,)
        bit = m & -m
        v = bit.bit_length() - 1
        left, right = rec(m ^ bit), rec(m & g[v])
        result = [0] * max(len(left), len(right) + 1)
        for i, c in enumerate(left):
            result[i] += c
        for i, c in enumerate(right):
            result[i + 1] += c
        return tuple(result)
    return rec(mask)


def enumerate_cliques(g, mask=None):
    """Enumerate cliques by increasing vertex sequences, independently of the recurrence."""
    if mask is None:
        mask = (1 << len(g)) - 1
    result = [0] * (mask.bit_count() + 1)

    def visit(available, size):
        result[size] += 1
        while available:
            bit = available & -available
            available ^= bit
            visit(available & g[bit.bit_length() - 1], size + 1)
    visit(mask, 0)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def q(g, mask=None):
    return sum((-1) ** i * c for i, c in enumerate(coefficients(g, mask)))


def parameters(family):
    require(family in ('3k8', '4k4', '6k6'), 'Unknown family')
    data = json.loads((ROOT / 'data' / f'family_{family}.json').read_text(encoding='utf-8'))
    g = from_lists(data['A'])
    require(data['n'] == len(g) and type(data['s']) is int and data['s'] >= 0, 'Invalid seed parameters')
    profiles = data['profiles']
    require(len(profiles) >= 1, 'At least one auxiliary type is required')
    for p in profiles:
        require(len(p) == len(set(p)) and all(type(v) is int and 0 <= v < len(g) for v in p), 'Invalid profile')
    from_edges(len(profiles), data['R'])
    return data


def layers(seed, profiles, type_edges, m):
    """Construct G_m by adding the six edge classes of the definition."""
    require(type(m) is int and m >= 0, 'The number of layers must be a non-negative integer')
    n, d = len(seed), len(profiles)
    labels = [('a', v) for v in range(n)] + [('c', i) for i in range(m)]
    labels += [('x', j, i) for i in range(m) for j in range(d)]
    g = [0] * len(labels)
    index = {v: i for i, v in enumerate(labels)}

    def add(u, v):
        require(u != v, 'Loop in construction')
        g[u] |= 1 << v
        g[v] |= 1 << u

    for u, v in edges(seed):
        add(u, v)
    for i in range(m):
        ci = index['c', i]
        for a in range(n):
            add(ci, a)
        for h in range(i):
            add(ci, index['c', h])
        for j, profile in enumerate(profiles):
            xi = index['x', j, i]
            for a in profile:
                add(xi, a)
            for h in range(i):
                add(xi, index['x', j, h])
            for h in range(m):
                if h != i:
                    add(ci, index['x', j, h])
    for j, t in type_edges:
        for i in range(m):
            for h in range(m):
                add(index['x', j, i], index['x', t, h])
    return validate(g), labels


def pairwise_layers(seed, profiles, type_edges, m):
    """Independent construction: decide adjacency for each unordered pair."""
    n, d = len(seed), len(profiles)
    labels = [('a', v) for v in range(n)] + [('c', i) for i in range(m)]
    labels += [('x', j, i) for i in range(m) for j in range(d)]
    r = {frozenset(e) for e in type_edges}

    def adjacent(u, v):
        if u[0] > v[0]:
            u, v = v, u
        if u[0] == 'a':
            if v[0] == 'a':
                return bool(seed[u[1]] >> v[1] & 1)
            return v[0] == 'c' or u[1] in profiles[v[1]]
        if u[0] == 'c':
            return v[0] == 'c' or u[1] != v[2]
        return u[1] == v[1] or frozenset((u[1], v[1])) in r

    es = [(i, j) for i, j in combinations(range(len(labels)), 2) if adjacent(labels[i], labels[j])]
    return from_edges(len(labels), es), labels


def family_graph(family, k, independent=False):
    require(type(k) is int and k >= 1, 'The level k must be an integer at least 1')
    p = parameters(family)
    seed = from_lists(p['A'])
    if k < p['s']:
        subset = p['prefix'][str(k)]
        return induced(seed, subset), [('a', v) for v in subset]
    constructor = pairwise_layers if independent else layers
    return constructor(seed, p['profiles'], p['R'], k - p['s'])


def membership(g, k, mask=None):
    """Exact finite recursion for small independent controls; no search limit.

    The certificate verifier does not call this function.
    """
    if mask is None:
        mask = (1 << len(g)) - 1

    @lru_cache(None)
    def rec(m, j):
        if not m:
            return False
        if cone(g, m) is not None:
            return True
        if j == -1:
            return False
        return any(rec(m & g[v], j - 1) and rec(m ^ (1 << v), j) for v in vertices(m))
    require(type(k) is int and k >= -1, 'Invalid dismantling level')
    return rec(mask, k)
