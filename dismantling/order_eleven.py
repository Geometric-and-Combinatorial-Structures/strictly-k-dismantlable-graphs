"""Finite verification for the minimum-order argument; see docs/minimum-orders.md."""
import json
from pathlib import Path
import sys
import time

from .graphs import ROOT, strict_json, require, membership, family_graph
from .reference import classify as reference_classify

if not __debug__:
    raise SystemExit('Run verification without -O or -OO.')

SEEDS = strict_json((ROOT/'data/minimum_order/seeds.json').read_text(encoding='utf-8'))
MISSING = [row['missing_edges'] for row in SEEDS]

def q(g):
    cache = {0: 1}
    def value(mask):
        if mask not in cache:
            v = mask.bit_length() - 1
            cache[mask] = value(mask ^ (1 << v)) - value(mask & g[v])
        return cache[mask]
    return value((1 << len(g)) - 1)

def seed(missing):
    require(len(missing) == len({tuple(e) for e in missing}), 'Repeated missing edge')
    require(all(type(u) is int and type(v) is int and 0 <= u < v < 8 for u,v in missing), 'Invalid missing edge')
    g = [255 ^ (1 << v) for v in range(8)]
    for u, v in missing:
        g[u] ^= 1 << v
        g[v] ^= 1 << u
    return g

def extend(g, s, t, edge):
    h = g + [0, 0, 0]
    for v in range(8):
        h[v] |= 1 << 8
        h[8] |= 1 << v
        if (s >> v) & 1:
            h[v] |= 1 << 9
            h[9] |= 1 << v
        if (t >> v) & 1:
            h[v] |= 1 << 10
            h[10] |= 1 << v
    if edge:
        h[9] |= 1 << 10
        h[10] |= 1 << 9
    return tuple(h)

def classify(h):
    if q(h):
        return 'nonzero_q'
    if membership(h, 0):
        return 'D0'
    if membership(h, 1):
        return 'strict1'
    if membership(h, 2):
        raise AssertionError(('strict2 counterexample', h))
    return 'zero_q_outside_D2'


def crosscheck(h, status):
    other, q_other = reference_classify(h)
    require(other == status and q_other == q(h), 'The independent extension classifications disagree')

def run():
    started = time.monotonic()
    expected = strict_json((ROOT/'data/minimum_order/expected_extensions.json').read_text(encoding='utf-8'))
    require(len(MISSING) == len(expected) == 7, 'Exactly seven seeds and expected rows are required')
    rows = []
    for i, missing in enumerate(MISSING, 1):
        g = seed(missing)
        assert membership(tuple(g), 1) and not membership(tuple(g), 0)
        counts = {s: 0 for s in ('nonzero_q','D0','strict1','zero_q_outside_D2')}
        diagonal = dict(counts)
        unordered = dict(counts)
        for s in range(256):
            for t in range(256):
                for edge in (False, True):
                    h = extend(g, s, t, edge)
                    status = classify(h)
                    counts[status] += 1
                    if s == t:
                        diagonal[status] += 1
                    if s <= t:
                        crosscheck(h,status)
                        unordered[status] += 1
        assert sum(counts.values()) == 131072
        assert sum(unordered.values()) == 65792
        assert all(counts[k] == 2*unordered[k]-diagonal[k] for k in counts)
        row = {'seed':i,'ordered':counts,'unordered':unordered,'diagonal':diagonal,
               'strict2':0}
        rows.append(row)
        require(row == expected[i-1], f'Extension counts differ for X_{i}')
        print(f'    X_{i}: 131,072 ordered choices; 65,792 after exchanging the two added vertices; no strict-level-two graph.', flush=True)
    witness, _ = family_graph('4k4', 2)
    assert len(witness) == 12 and membership(witness, 2) and not membership(witness, 1)
    result = {'status':'PASS','ordered_candidates':917504,'unordered_candidates':460544,
              'independently_classified_unordered_candidates':460544,
              'rows':rows,'H2_strict_level':2,'H2_order':12,
              'seconds':round(time.monotonic()-started,3),
              'scope':'Only the two-external-vertices case. The coverage argument and the one-external-vertex case are explained in supplement Section 8 and docs/minimum-orders.md.'}
    return result
