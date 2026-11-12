"""Finite verification for the minimum-order argument; see docs/minimum-orders.md."""
import json
from pathlib import Path
import sys

from .graphs import ROOT, strict_json, require, family_graph, induced, membership, q, enumerate_cliques

if not __debug__:
    raise SystemExit('Run verification without -O or -OO.')

FOLDS = {4: [(11, 5), (13, 5), (6, 12)], 8: [(9, 2), (6, 12)],
         10: [(5, 4), (11, 3)], 12: [(5, 4), (7, 8)]}


def fold_sequence(adj, vertices, sequence, survivor=None):
    alive = set(vertices)
    for u, v in sequence:
        assert u != v and u in alive and v in alive, ('invalid fold endpoints', u, v)
        assert (adj[u] | {u}) & alive <= (adj[v] | {v}) & alive, ('invalid domination', u, v)
        alive.remove(u)
    if survivor is not None:
        assert alive == {survivor}
    return alive


def run():
    g, labels = family_graph('4k4', 2)
    labels = [int(v[1]) for v in labels]
    assert labels == list(range(2, 14))
    adj = {labels[u]: {labels[v] for v in range(len(g)) if g[u] >> v & 1}
           for u in range(len(g))}
    vertices = set(labels)
    H1 = adj[7]
    assert H1 == {2, 4, 5, 8, 9, 10, 12, 13}
    path = [8, 2, 13, 5]
    assert adj[9] & H1 == set(path)
    assert {(u, v) for u in path for v in path if u < v and v in adj[u]} == {(2, 8), (2, 13), (5, 13)}
    S = fold_sequence(adj, H1 - {9}, [(5, 4), (12, 8)])
    assert (adj[10] | {10}) & S == S
    T = fold_sequence(adj, vertices - {7}, [(10, 3)])
    assert adj[4] & T == {3, 5, 6, 8, 11, 12, 13}
    S = fold_sequence(adj, adj[4] & T, [(8, 12)])
    assert (adj[5] | {5}) & S == S
    S = fold_sequence(adj, T - {4}, [(8, 2), (13, 9)])
    assert (adj[11] | {11}) & S == S
    permutation = {v: v for v in labels}
    for u, v in [(4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]:
        permutation[u], permutation[v] = v, u
    assert all((v in adj[u]) == (permutation[v] in adj[permutation[u]]) for u in labels for v in labels)
    representatives = {2, 3, 4, 7, 8, 10, 12}
    assert representatives | {permutation[v] for v in representatives} == vertices
    octahedra = {}
    for v, sequence in FOLDS.items():
        S = fold_sequence(adj, adj[v], sequence)
        assert len(S) == 6 and all(len(adj[u] & S) == 4 for u in S)
        octahedra[v] = sorted(S)
    values = {}
    for i, v in enumerate(labels):
        h = induced(g, [j for j in range(len(g)) if g[i] >> j & 1])
        # Independent clique enumeration cross-checks the recurrence value.
        counts = enumerate_cliques(h)
        value = sum((-1)**j * c for j, c in enumerate(counts))
        assert value == q(h)
        expected = -2 if v in {2, 3} else 0 if v in {6, 7} else -1
        assert value == expected
        values[v] = value
        if v in {2, 3, 6, 7}:
            S = adj[v]
            assert all(not ((adj[u] | {u}) & S <= (adj[w] | {w}) & S)
                       for u in S for w in S if u != w)
    assert membership(g, 2) and not membership(g, 1)
    rejected = 0
    try:
        fold_sequence(adj, vertices - {6}, [(11, 2)])
    except AssertionError:
        rejected += 1
    try:
        fold_sequence(adj, vertices - {7}, [(10, 3)], 12)
    except AssertionError:
        rejected += 1
    assert rejected == 2
    result = {'status': 'PASS', 'order': 12, 'strict_level': 2,
              'path': path, 'fold_sequences': FOLDS, 'q_values': values,
              'no_dominated_vertex_in_neighbourhoods': [2, 3, 6, 7],
              'octahedral_remainders': octahedra,
              'automorphism': permutation,
              'deliberately_invalid_target_and_survivor_rejected': rejected,
              'scope': 'The explicit reduction, symmetry and neighbourhood obstructions for H_2 in the identified article. Supplement Section 4 also provides its complete recursive certificates.'}
    return result
