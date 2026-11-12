"""Extended completeness check for the supplied small-graph catalogues."""
from collections import defaultdict
from itertools import combinations, permutations
from math import factorial
from .graphs import ROOT, require, from_graph6, strict_json
from .small_orders import isomorphism


def unlabelled_count(n):
    """Burnside's lemma for the action of vertex permutations on edge sets."""
    pairs = list(combinations(range(n),2))
    index = {pair:i for i,pair in enumerate(pairs)}
    total = 0
    for perm in permutations(range(n)):
        image = [index[tuple(sorted((perm[u],perm[v])))] for u,v in pairs]
        seen, orbits = set(), 0
        for start in range(len(pairs)):
            if start in seen:
                continue
            orbits += 1
            k = start
            while k not in seen:
                seen.add(k)
                k = image[k]
        total += 2**orbits
    require(total % factorial(n) == 0, 'Non-integral Burnside count')
    return total // factorial(n)


def invariant(g):
    """Isomorphism-invariant buckets; no completeness assumption enters here."""
    degree = [row.bit_count() for row in g]
    values=[]
    for v in range(len(g)):
        ns = [u for u in range(len(g)) if g[v] >> u & 1]
        triangles = sum(bool(g[u] >> w & 1) for u,w in combinations(ns,2))
        values.append((degree[v],triangles,tuple(sorted(degree[u] for u in ns))))
    return len(g),tuple(sorted(values))


def run():
    buckets = defaultdict(list)
    counts = [0]*9
    comparisons=0
    for name in ['graphs0to6.g6','graph7.g6','graph8.g6']:
        for line in (ROOT/'data/catalogues'/name).read_text(encoding='ascii').splitlines():
            g = from_graph6(line)
            require(len(g) <= 8,'Unexpected graph order')
            key = invariant(g)
            for h in buckets[key]:
                comparisons += 1
                require(isomorphism(g,h) is None,'Two catalogue entries are isomorphic')
            buckets[key].append(g)
            counts[len(g)] += 1
    burnside = [unlabelled_count(n) for n in range(9)]
    require(counts == burnside,'The catalogues do not contain every isomorphism class')
    return {'orders':list(range(9)),'catalogue_counts':counts,'burnside_counts':burnside,
            'pairwise_nonisomorphic':True,'exact_isomorphism_comparisons':comparisons,
            'scope':'Completeness up to isomorphism of all supplied graphs of orders 0 through 8.'}
