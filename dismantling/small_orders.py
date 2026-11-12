"""Finite verification for the minimum-order argument; see docs/minimum-orders.md."""
import hashlib
import json
from pathlib import Path
import sys
import time

from .graphs import ROOT, strict_json, require, from_graph6, membership
from .homology import betti
from .reference import classify as reference_classify
from .order_eleven import MISSING, seed

if not __debug__:
    raise SystemExit('Run verification without -O or -OO.')

SEEDS = strict_json((ROOT/'data/minimum_order/seeds.json').read_text(encoding='utf-8'))
CERTIFICATES = [(r['first'], r['path'], r['folds'], r['apex']) for r in SEEDS]


def printed_certificates(graphs):
    require(len(graphs) == len(CERTIFICATES) == 7, 'Incomplete seed reductions')
    rows = []
    for g, (first, path, folds, apex) in zip(graphs, CERTIFICATES):
        # Check the complete neighbourhood, every path edge and every non-edge.
        assert g[first] == sum(1 << v for v in path)
        assert all(bool(g[u] >> v & 1) == (abs(i-j) == 1)
                   for i, u in enumerate(path) for j, v in enumerate(path))
        full = (1 << len(g)) - 1
        closed = [g[u] | 1 << u for u in range(len(g))]
        assert not any(closed[u] & ~closed[v] == 0
                       for u in range(len(g)) for v in range(len(g)) if u != v)
        alive = full ^ (1 << first)
        for u, v in folds:
            assert u != v and alive >> u & 1 and alive >> v & 1
            assert (closed[u] & alive) & ~(closed[v] & alive) == 0
            alive ^= 1 << u
        assert alive >> apex & 1 and closed[apex] & alive == alive
        degree_four = [v for v in range(len(g)) if g[v].bit_count() == 4]
        mask = sum(1 << v for v in degree_four)
        rows.append({'first': first, 'path': path, 'folds': folds, 'apex': apex,
                     'edges': sum(x.bit_count() for x in g)//2,
                     'degree_four_vertices': degree_four,
                     'induced_degrees': sorted((g[v] & mask).bit_count() for v in degree_four)})
    assert [r['edges'] for r in rows] == [17, 18, 18, 18, 18, 19, 19]
    assert [r['induced_degrees'] for r in rows[1:5]] == [[1,1,1,1], [0,1,1,2], [1,1,2,2], [2,2,2,2]]
    assert rows[5]['induced_degrees'] == [0,0] and rows[6]['induced_degrees'] == [1,1]
    return rows


def isomorphism(g, h):
    """Find a bijection preserving every edge and non-edge, or return None."""
    if len(g) != len(h):
        return None
    n = len(g)
    degree_g, degree_h = [x.bit_count() for x in g], [x.bit_count() for x in h]
    if sorted(degree_g) != sorted(degree_h):
        return None
    candidates = [[v for v in range(n) if degree_g[u] == degree_h[v]] for u in range(n)]
    order = sorted(range(n), key=lambda u: (len(candidates[u]), -degree_g[u]))
    mapping, used = {}, set()

    def extend(i):
        if i == n:
            return dict(mapping)
        u = order[i]
        for v in candidates[u]:
            if v in used or any(((g[u] >> a) & 1) != ((h[v] >> b) & 1)
                                for a, b in mapping.items()):
                continue
            mapping[u] = v
            used.add(v)
            found = extend(i + 1)
            if found is not None:
                return found
            used.remove(v)
            del mapping[u]
        return None

    result = extend(0)
    if result is not None:
        assert sorted(result.values()) == list(range(n))
        assert all(((g[u] >> v) & 1) == ((h[result[u]] >> result[v]) & 1)
                   for u in range(n) for v in range(n))
    return result


def run():
    started = time.monotonic()
    rows = [{'order': n, 'graphs': 0, 'D0': 0, 'strict1': 0, 'F2_acyclic': 0}
            for n in range(9)]
    classes, catalogues = [], []
    seen_codes = set()
    provenance = {r['file']:r for r in strict_json((ROOT/'data/catalogues/provenance.json').read_text(encoding='utf-8'))}
    for name in ['graphs0to6.g6', 'graph7.g6', 'graph8.g6']:
        path = ROOT / 'data/catalogues' / name
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == provenance[name]['sha256'], 'Catalogue source hash differs')
        require(len(raw.decode().splitlines()) == provenance[name]['graphs'], 'Catalogue source size differs')
        catalogues.append({'file': name, 'sha256': hashlib.sha256(raw).hexdigest()})
        for line in raw.decode().splitlines():
            require(line not in seen_codes, 'Repeated catalogue entry')
            seen_codes.add(line)
            g = from_graph6(line)
            require(len(g) <= 8, 'Catalogue graph outside orders 0 through 8')
            n = len(g)
            row = rows[n]
            row['graphs'] += 1
            d0, d1 = membership(g, 0), membership(g, 1)
            category, _ = reference_classify(g)
            require((category == 'D0') == d0 and (category in ('D0','strict1')) == d1,
                    'Independent small-order membership decisions disagree')
            acyclic = not betti(g, independent=True)
            assert not acyclic or d1, ('acyclic graph outside D1', line)
            assert not d1 or acyclic, ('D1 graph not acyclic', line)
            if n < 8:
                assert not d1 or d0, ('smaller graph of strict level one', line)
            row['D0'] += d0
            row['strict1'] += d1 and not d0
            row['F2_acyclic'] += acyclic
            if d1 and not d0:
                classes.append((line, g))
    assert [r['graphs'] for r in rows] == [1, 1, 2, 4, 11, 34, 156, 1044, 12346]
    assert sum(r['graphs'] for r in rows) == 13599
    assert len(classes) == 7
    printed = [tuple(seed(m)) for m in MISSING]
    certificates = printed_certificates(printed)
    assert all(isomorphism(g, h) is None for i, g in enumerate(printed)
               for h in printed[i + 1:])
    correspondence = []
    for i, g in enumerate(printed, 1):
        matches = [(code, isomorphism(g, h)) for code, h in classes]
        matches = [(code, mapping) for code, mapping in matches if mapping is not None]
        assert len(matches) == 1
        code, mapping = matches[0]
        correspondence.append({'printed_graph': i, 'catalogue_graph6': code,
                               'isomorphism': mapping})
    assert len({r['catalogue_graph6'] for r in correspondence}) == 7
    from .graphs import family_graph
    h1, _ = family_graph('4k4', 1)
    h1_matches = [(i, isomorphism(h1,g)) for i,g in enumerate(printed,1)]
    h1_matches = [(i,m) for i,m in h1_matches if m is not None]
    require(len(h1_matches) == 1, 'H_1 does not match exactly one of the seven graphs')
    assert betti((), independent=True) == {-1: 1}
    assert not any(membership((), j) for j in [-1, 0, 1, 2])
    result = {'status': 'PASS', 'catalogues': catalogues, 'orders': rows,
              'pairwise_nonisomorphic': True, 'correspondence': correspondence,
              'independent_decisions_compared': sum(r['graphs'] for r in rows),
              'printed_reductions_and_invariants': certificates,
              'H1_correspondence':{'graph':h1_matches[0][0], 'isomorphism':h1_matches[0][1]},
              'homology': 'Reduced homology over F_2, including degree -1',
              'seconds': round(time.monotonic() - started, 3),
              'scope': 'All supplied catalogue entries, orders 0 through 8. The separate catalogue-completeness group establishes completeness; no inference about higher orders.'}
    return result
