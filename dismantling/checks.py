"""Finite checks organised by the mathematical assertions they support."""
from itertools import combinations, product
from collections import Counter
import copy
import json
import re
from .graphs import (ROOT, require, from_lists, from_edges, edges, induced, cone, fold,
                     coefficients, enumerate_cliques, q, parameters, layers,
                     pairwise_layers, family_graph, membership, vertices)
from .homology import betti
from .certificates import verify_4k4, read_certificate


def secondary_tables(family):
    folder = ROOT / 'supplement' / 'tables' / family
    p = parameters(family)
    a = from_lists(p['A'])
    text = (folder / 'adjacency.tex').read_text()
    rows = re.findall(r'^(\d+)\s*&([^\n]+)', text, re.M)
    parsed = []
    for v, ns in rows:
        require(int(v) == len(parsed), 'Adjacency table labels out of order')
        parsed.append(list(map(int, re.findall(r'\d+', ns))))
    require(from_lists(parsed) == a, 'Supplement adjacency table differs from data')
    profile_text = (folder / 'profiles.tex').read_text()
    profiles = []
    for line in profile_text.splitlines():
        if not re.match(r'^\d+\s*&', line):
            continue
        cols = line.split('&')
        require(int(cols[0]) == len(profiles), 'Profile rows out of order')
        nums = list(map(int, re.findall(r'\d+', cols[1])))
        if family == '4k4':
            nums = sorted(set(range(len(a))) - set(nums))
            require(len(nums) == int(cols[2].removesuffix(r'\\')), 'Wrong profile size')
        profiles.append(nums)
    require(profiles == p['profiles'], 'Profile table differs from data')
    return folder, p, a


def numeric_rows(path, columns):
    rows = []
    for line in path.read_text().splitlines():
        if not re.match(r'^\d+\s*&', line):
            continue
        fields = line.removesuffix(r'\\').split('&')
        values = [int(v.strip().strip('$')) for v in fields]
        require(len(values) == columns, 'Wrong table width')
        rows.append(values)
    return rows


def check_4k4():
    folder, p, a = secondary_tables('4k4')
    params = json.loads((ROOT / 'data/certificates/PARAMETERS.json').read_text())
    require(a == from_lists(params['A_adjacency_lists']) and p['s'] == params['base_level'], 'Generator seed mismatch')
    require(p['profiles'] == params['profile_vertex_sets'] and p['R'] == params['R_edges'], 'Generator profiles mismatch')
    prefix = json.loads((ROOT / 'data/certificates/PREFIX.json').read_text())
    for k in ('1', '2'):
        require(p['prefix'][k] == prefix['levels'][k]['vertices_in_A16'], 'Generator prefix mismatch')
    result = verify_4k4()
    c = read_certificate('FINITE_CERTIFICATE.json.gz')
    rows = []
    for line in (folder / 'cliques.tex').read_text().splitlines():
        if not line.startswith((r'\(a_', r'\(x_')):
            continue
        fields = line.removesuffix(r'\\').split('&')
        label = int(re.search(r'\d+', fields[0])[0])
        if fields[0].startswith(r'\(x_'):
            label += 17
        rows.append([label, *[int(x.strip().strip('$')) for x in fields[1:]]])
    expected = [[r['v'], *r['coefficients'][:8], r['q']] for r in c['q_rows']]
    require(rows == expected, 'The 19 printed clique rows do not match their certificates')
    # Direct proof of H_1 in original seed labels.
    mask = sum(1 << v for v in p['prefix']['1'])
    for v, inner, target, apex in [(5, 9, 13, 4), (4, 12, 8, 10)]:
        link = fold(a, mask & a[v], inner, target)
        require(apex in set(vertices(link)) and link & ~(a[apex] | (1 << apex)) == 0, 'Invalid prefix cone')
        mask ^= 1 << v
    require(cone(a, mask) == 2, 'Invalid prefix remainder')
    h1, _ = family_graph('4k4', 1)
    require(all(cone(h1, ns) is None for ns in h1), 'Unexpected first fold in H_1')
    require(membership(h1, 1) and not membership(h1, 0), 'Independent prefix classification differs')
    result['direct_prefix_proof'] = True
    return result


def check_6k6():
    folder, p, a = secondary_tables('6k6')
    data = json.loads((ROOT / 'data/seed_6k6_original.json').read_text())
    require(a == from_lists(data['A']) and p['profiles'] == data['P'] and p['R'] == data['R'], 'Seed witness mismatch')
    b, _ = layers(a, p['profiles'], p['R'], 1)
    require(len(edges(a)) == 47 and len(edges(b)) == 114, 'Wrong edge counts')
    inclusions = []
    for name, start, rows, final, tip, table in [
        ('A', set(range(12)), data['TA'], [5, 6, 8, 9, 10, 11], 9, 'certificate_a.tex'),
        ('B-p', set(range(18)) - {12}, data['TB'], [3, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17], 11, 'certificate_b.tex'),
    ]:
        mask = sum(1 << v for v in start)
        for v, expected, folds, apex in rows:
            require(mask >> v & 1, 'Outer vertex already absent')
            link = mask & b[v]
            require(list(vertices(link)) == expected, 'Incorrect current neighbourhood')
            for u, t in folds:
                inclusions.append((name, v, u, t, list(vertices((b[u] | (1 << u)) & link)),
                                   list(vertices((b[t] | (1 << t)) & link))))
                link = fold(b, link, u, t)
            require(link >> apex & 1 and link & ~(b[apex] | (1 << apex)) == 0, 'Invalid inner cone')
            mask ^= 1 << v
        require(list(vertices(mask)) == final and mask & ~(b[tip] | (1 << tip)) == 0, 'Invalid final cone')
        printed = []
        for line in (folder / table).read_text().splitlines():
            if not re.match(r'^\d+\s*&', line):
                continue
            fields = line.removesuffix(r'\\').split('&')
            ns = re.search(r'\\\{([0-9,]+)\\\}', fields[1])
            fs = [list(map(int, z)) for z in re.findall(r'(\d+)\\to\s*(\d+)', fields[2])]
            printed.append([int(fields[0]), list(map(int, ns[1].split(','))), fs, int(fields[3])])
        require(printed == rows, 'Printed positive witness differs')
    printed = []
    for line in (folder / 'inclusions.tex').read_text().splitlines():
        if not line.startswith(('$A$;', '$B-p$;')):
            continue
        name, outer = line.split('&', 1)[0].split(';')
        f = re.search(r'(\d+)\\to\s*(\d+)', line)
        sets = re.findall(r'\\\{([0-9,]+)\\\}', line)
        printed.append((name.strip('$'), int(outer), int(f[1]), int(f[2]), *[list(map(int, s.split(','))) for s in sets]))
    require(printed == inclusions and len(inclusions) == 14, 'Printed closed neighbourhoods differ')
    degrees = [[v, ns.bit_count(), ns.bit_count() - 1,
                max((a[u] & ns).bit_count() for u in vertices(ns))] for v, ns in enumerate(a)]
    require(numeric_rows(folder / 'degrees.tex', 4) == degrees and all(r[3] < r[2] for r in degrees), 'First-fold obstruction fails')
    rows = []
    for v, ns in enumerate(b):
        if v == 12:
            continue
        co = coefficients(b, ns)
        require(co == enumerate_cliques(b, ns) and len(co) <= 7, 'Clique counts disagree')
        value = q(b, ns)
        require(value == (2 if v in (7, 15) else 1), 'Euler obstruction differs')
        rows.append([v, *co, *([0] * (7 - len(co))), value])
    require(numeric_rows(folder / 'cliques.tex', 9) == rows, 'Printed clique table differs')
    return {'outer_deletions': 12, 'inner_folds': 14, 'negative_degree_rows': 12, 'clique_rows': 17}


def compare_constructions():
    result = []
    for family in ('3k8', '4k4', '6k6'):
        p = parameters(family)
        for k in range(1, 7):
            g, labels = family_graph(family, k)
            other, other_labels = family_graph(family, k, independent=True)
            require((g, labels) == (other, other_labels), 'Independent constructions differ')
            order = {'3k8': 3 * k + 8, '4k4': 4 * k + 4, '6k6': 6 * k + 6}[family]
            require(len(g) == order, 'Incorrect order')
            if k >= p['s']:
                m = k - p['s']
                if family == '4k4':
                    require(len(edges(g)) == 97 + 53 * m + 7 * m * m, 'Incorrect edge polynomial')
                if family == '6k6':
                    require(len(edges(g)) == 47 + 52 * m + 15 * m * m, 'Incorrect edge polynomial')
            result.append({'family': family, 'k': k, 'vertices': len(g), 'edges': len(edges(g))})
    return {'examples': result}


def check_kernels():
    a, _ = family_graph('3k8', 1)
    h = from_edges(11, [e for e in edges(a) if e != (1, 2)])
    require(len(edges(h)) == 32 and from_edges(11, sorted(edges(h) + [(1, 2)])) == a, 'Kernel completion fails')
    p = parameters('3k8')
    b, _ = layers(a, p['profiles'], p['R'], 1)
    require(betti(h, True) == {}, 'Kernel not acyclic over F_2')
    shifts = []
    for v in range(11):
        before = betti(induced(h, list(vertices(h[v]))), True)
        after = betti(induced(b, list(vertices(b[v]))), True)
        require(before == {1: 2 if v == 10 else 1}, 'Printed kernel Betti numbers differ')
        require(before and after == {i + 1: rank for i, rank in before.items()}, 'Kernel link shift fails')
        shifts.append({'vertex': v, 'kernel_link_betti': before, 'extension_link_betti': after})
    common = h[1] & h[2]
    c = induced(h, list(vertices(common)))
    require(membership(c, 0), 'Common-neighbour graph is not dismantlable')
    require(q(b) == -q(h) and q(b, ((1 << len(b)) - 1) ^ (1 << 11)) == q(a) - q(h), 'Global kernel identities fail')
    for j in (0, 1):
        profile_graph = induced(a, p['profiles'][1 - j])
        require(betti(induced(b, list(vertices(b[12 + j])))) == {i + 1: r for i, r in betti(profile_graph).items()}, 'Auxiliary kernel shift fails')
    return {'seed_edges': 33, 'kernel_edges': 32, 'kernel_reduced_betti': {}, 'links': shifts,
            'common_neighbours': list(vertices(common)), 'common_neighbour_graph_in_D0': True}


def boundaries():
    empty, singleton, cycle = (), (0,), from_edges(5, [(0, 1), (0, 3), (1, 2), (2, 3)])
    require(betti(empty, True) == {-1: 1} and q(empty) == 1, 'Empty-complex convention fails')
    require(betti(singleton, True) == {} and q(singleton) == 0, 'Cone convention fails')
    require(betti(cycle, True) == {0: 1, 1: 1} and q(cycle) == 0, 'Euler-zero example fails')
    for k in range(-1, 3):
        require(not membership(empty, k) and membership(singleton, k), 'Boundary membership fails')
    seed, profiles = (0,), [[]]
    for m in (1, 2, 3):
        g, labs = layers(seed, profiles, [], m)
        v = labs.index(('x', 0, 0))
        require(betti(induced(g, list(vertices(g[v]))), True) == {m - 2: 1}, 'Empty auxiliary link shift fails')
    return {'empty_graph': {'q': 1, 'reduced_betti': {-1: 1}},
            'C4_disjoint_K1': {'q': 0, 'reduced_betti': {0: 1, 1: 1}}, 'empty_auxiliary_layers': [1, 2, 3]}


def mutation_controls():
    original = read_certificate('FINITE_CERTIFICATE.json.gz')
    tests = []

    def reject(name, change):
        c = copy.deepcopy(original)
        change(c)
        try:
            verify_4k4(c=c)
        except (ValueError, KeyError, TypeError, IndexError):
            tests.append(name)
        else:
            raise ValueError('A deliberately invalid certificate was accepted: ' + name)

    def edge(c):
        c['A'][0] ^= 1 << 1
        c['A'][1] ^= 1 << 0

    reject('changed seed edge', edge)
    reject('wrong root level', lambda c: c['A_nodes'][c['A_positive_root']].update(k=4))
    reject('wrong root subset', lambda c: c['A_nodes'][c['A_positive_root']].update(m=3))
    reject('wrong positive root', lambda c: c.update(A_positive_root=c['A_negative_root']))
    reject('missing negative branch', lambda c: c['A_nodes'][c['A_negative_root']]['obstructions'].pop())
    reject('missing dependency', lambda c: c['A_nodes'][c['A_positive_root']].update(link='missing'))
    reject('circular dependency', lambda c: c['A_nodes'][c['A_positive_root']].update(link=c['A_positive_root']))
    reject('changed clique coefficient', lambda c: c['q_rows'][0]['coefficients'].__setitem__(1, 999))
    reject('false negative root value', lambda c: c['A_nodes'][c['A_negative_root']].update(value=True))
    reject('out-of-range adjacency bit', lambda c: c['A'].__setitem__(0, c['A'][0] | (1 << 16)))
    prefix = read_certificate('PREFIX_CERTIFICATES.json.gz')
    prefix['1']['nodes'][prefix['1']['positive_root']]['k'] = 2
    try:
        verify_4k4(prefix=prefix)
    except ValueError:
        tests.append('wrong prefix level')
    else:
        raise ValueError('A changed prefix level was accepted')
    p = parameters('3k8')
    seed = from_lists(p['A'])
    g, labels = layers(seed, p['profiles'], p['R'], 2)
    ci, xi = labels.index(('c', 0)), labels.index(('x', 0, 0))
    mutant = list(g)
    mutant[ci] |= 1 << xi
    mutant[xi] |= 1 << ci
    expected, _ = pairwise_layers(seed, p['profiles'], p['R'], 2)
    require(tuple(mutant) != expected, 'The altered centre incidence was not detected')
    tests.append('centre joined to its own auxiliary')
    return {'rejected': tests, 'count': len(tests)}


def deletion_controls():
    result = []
    for k in (2, 3, 4):
        g, labels = family_graph('3k8', k)
        full = (1 << len(g)) - 1
        require(q(g) == 0, 'The family graph has unexpected Euler obstruction')
        central, noncentral = 0, 0
        for v, label in enumerate(labels):
            if label[0] == 'c':
                mask = full ^ (1 << v)
                if k == 2:
                    raw = json.loads((ROOT / 'data/article_remainder.json').read_text())
                    index = {str(i): i for i in range(11)} | {'x': 12, 'y': 13}
                    for u, t in raw['folds']:
                        mask = fold(g, mask, index[u], index[t])
                else:
                    for j in range(2):
                        for h in range(k - 1):
                            if h != label[1]:
                                mask = fold(g, mask, labels.index(('x', j, h)), labels.index(('x', j, label[1])))
                require(cone(g, mask) is not None, 'A centre-deleted graph did not reduce to a cone')
                central += 1
            else:
                require(q(g, full ^ (1 << v)) == q(g, g[v]) != 0, 'Single-vertex deletion obstruction fails')
                noncentral += 1
        result.append({'k': k, 'centre_deletions_in_D0': central, 'other_single_deletions_with_nonzero_q': noncentral})
    return {'tested_levels': result, 'scope': 'One vertex deleted at a time, at levels 2, 3 and 4.'}


def template_controls(extended=False):
    count = Counter()
    max_n = 3 if extended else 1
    for n in range(1, max_n + 1):
        pairs = list(combinations(range(n), 2))
        for bits in range(1 << len(pairs)):
            seed = from_edges(n, [e for i, e in enumerate(pairs) if bits >> i & 1])
            for d in (1, 2):
                for rb in range(1 << (d * (d - 1) // 2)):
                    re = [(0, 1)] if rb else []
                    subsets = [list(vertices(s)) for s in range(1 << n)]
                    for profiles in product(subsets, repeat=d):
                        count['templates'] += 1
                        base, bl = layers(seed, profiles, re, 1)
                        bq = {v: q(base, base[i]) for i, v in enumerate(bl) if v[0] != 'c'}
                        bh = {v: betti(induced(base, list(vertices(base[i])))) for i, v in enumerate(bl) if v[0] != 'c'} if n <= 2 else {}
                        for m in range(4):
                            g, labels = layers(seed, profiles, re, m)
                            require((g, labels) == pairwise_layers(seed, profiles, re, m), 'Independent generic construction differs')
                            count['orders'] += 1
                            for i in range(m):
                                c = labels.index(('c', i))
                                ns = list(vertices(g[c]))
                                renamed = [lab if lab[0] == 'a' else lab[:-1] + (lab[-1] - (lab[-1] > i),) for lab in [labels[v] for v in ns]]
                                old, old_labels = layers(seed, profiles, re, m - 1)
                                require(induced(g, ns) == old and renamed == old_labels, 'Central neighbourhood isomorphism fails')
                                count['central_isomorphisms'] += 1
                                if m >= 2:
                                    mask = ((1 << len(g)) - 1) ^ (1 << c)
                                    for j in range(d):
                                        for h in range(m):
                                            if h != i:
                                                mask = fold(g, mask, labels.index(('x', j, h)), labels.index(('x', j, i)))
                                                count['folds'] += 1
                                    require(cone(g, mask) is not None, 'Centre-deleted graph has no final cone')
                                    count['cone_remainders'] += 1
                            for v, label in enumerate(labels):
                                if not m or label[0] == 'c':
                                    continue
                                key = label if label[0] == 'a' else ('x', label[1], 0)
                                require(q(g, g[v]) == (-1) ** (m - 1) * bq[key], 'Euler sign identity fails')
                                count['euler_identities'] += 1
                                if n <= 2:
                                    link = induced(g, list(vertices(g[v])))
                                    actual = betti(link)
                                    require(actual == {i + m - 1: r for i, r in bh[key].items()}, 'Homology shift fails')
                                    require(q(link) == sum((-1) ** (i + 1) * r for i, r in actual.items()), 'Euler and homology disagree')
                                    count['homology_shifts'] += 1
    return {'seed_orders': list(range(1, max_n + 1)), 'auxiliary_types': [1, 2], 'layers': [0, 1, 2, 3],
            'coverage': 'All labelled seeds, profiles and type graphs in the indicated ranges; homology for seed order at most 2.',
            'counts': dict(count)}


def kernel_controls():
    count = Counter()
    for n in range(1, 4):
        pairs = list(combinations(range(n), 2))
        for bits in range(1 << len(pairs)):
            a = from_edges(n, [e for i, e in enumerate(pairs) if bits >> i & 1])
            for membership_pattern in product(range(3), repeat=n):
                # Each vertex belongs to S only, T only, or both.
                s = [v for v, state in enumerate(membership_pattern) if state != 1]
                t = [v for v, state in enumerate(membership_pattern) if state != 0]
                left, right, z = set(s) - set(t), set(t) - set(s), sorted(set(s) & set(t))
                h = from_edges(n, [(u, v) for u, v in edges(a)
                                   if not (u in left and v in right or u in right and v in left)])
                b, _ = layers(a, [s, t], [(0, 1)], 1)
                rest = induced(b, [v for v in range(len(b)) if v != n])
                count['covered_profiles'] += 1
                require(q(b) == -q(h) and q(rest) == q(a) - q(h), 'Global Euler kernel identity fails')
                require(betti(b) == {i + 1: r for i, r in betti(h).items()}, 'Global homology kernel shift fails')
                if not betti(a):
                    require(betti(rest) == {i + 1: r for i, r in betti(h).items()}, 'Remainder homology kernel shift fails')
                for v in range(n):
                    lh, lb = induced(h, list(vertices(h[v]))), induced(b, list(vertices(b[v])))
                    require(q(lb) == -q(lh), 'Original-vertex Euler kernel identity fails')
                    require(betti(lb) == {i + 1: r for i, r in betti(lh).items()}, 'Original-vertex homology kernel shift fails')
                    count['original_neighbourhoods'] += 1
                for j, own, opposite in [(0, s, t), (1, t, s)]:
                    lb = induced(b, list(vertices(b[n + 1 + j])))
                    require(q(lb) == q(induced(a, own)) - q(induced(a, z)), 'Auxiliary Euler kernel identity fails')
                    if not betti(h):
                        require(betti(lb) == {i + 1: r for i, r in betti(induced(a, opposite)).items()}, 'Auxiliary homology kernel shift fails')
                        count['acyclic_kernel_auxiliary_shifts'] += 1
    return {'seed_orders': [1, 2, 3], 'coverage': 'All labelled graphs and all ordered pairs of profiles covering their vertices.', 'counts': dict(count)}
