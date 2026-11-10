"""Verify finite recursive proofs without searching for a dismantling order."""
import gzip
from itertools import combinations
from .graphs import ROOT, require, validate, from_lists, from_edges, from_graph6, layers, induced, coefficients, enumerate_cliques, vertices, strict_json


def read_certificate(name):
    with gzip.open(ROOT / 'data' / 'certificates' / name, 'rt', encoding='utf-8') as stream:
        return strict_json(stream.read())


def check_nodes(g, nodes, root, expected_mask, expected_level, expected_value):
    """Bind the root to the claimed graph, subset, level and Boolean value.

    Children are checked in their current induced subgraphs. Every false
    non-cone state covers every possible first deletion. Repeated states may
    share a proof, but circular dependencies are rejected.
    """
    validate(g)
    require(root in nodes, 'Missing root')
    z = nodes[root]
    require((z['m'], z['k']) == (expected_mask, expected_level), 'Root is not the claimed state')
    require(z['value'] is expected_value, 'Wrong root truth value')
    checked, active = {}, set()

    def visit(key):
        require(key in nodes, 'Missing proof dependency')
        require(key not in active, 'Circular proof dependency')
        if key in checked:
            return checked[key]
        active.add(key)
        state = nodes[key]
        mask, level, truth = state['m'], state['k'], state['value']
        require(type(mask) is int and 0 <= mask < 1 << len(g), 'Invalid subset')
        require(type(level) is int and level >= -1 and type(truth) is bool, 'Invalid state')
        vs = set(vertices(mask))
        apices = {v for v in vs if mask & ~(g[v] | (1 << v)) == 0}
        rule = state['rule']

        def child(child_key, m, k, value):
            require(child_key in nodes, 'Missing proof dependency')
            c = nodes[child_key]
            require((c['m'], c['k']) == (m, k), 'Child is not the required induced state')
            require(m.bit_count() < mask.bit_count(), 'A child must have fewer vertices')
            require(visit(child_key) is value, 'Wrong child truth value')

        if rule == 'empty':
            require(not vs and truth is False, 'Invalid empty state')
        elif rule == 'cone':
            require(type(state['apex']) is int and state['apex'] in apices and truth is True, 'Invalid cone')
        elif rule == 'not_cone':
            require(vs and not apices and level == -1 and truth is False, 'Invalid non-cone')
        elif rule == 'delete':
            v = state['vertex']
            require(type(v) is int and v in vs and level >= 0 and truth is True, 'Invalid deletion')
            child(state['link'], mask & g[v], level - 1, True)
            child(state['rest'], mask ^ (1 << v), level, True)
        elif rule == 'blocked':
            require(vs and not apices and level >= 0 and truth is False, 'Invalid negative state')
            obs = state['obstructions']
            require(all(type(o['vertex']) is int for o in obs), 'Invalid obstruction vertex')
            require(len(obs) == len(vs) and {o['vertex'] for o in obs} == vs, 'Incomplete negative coverage')
            for o in obs:
                v = o['vertex']
                require(o['side'] in ('link', 'rest'), 'Invalid obstruction side')
                m, k = (mask & g[v], level - 1) if o['side'] == 'link' else (mask ^ (1 << v), level)
                child(o['child'], m, k, False)
        else:
            raise ValueError('Unknown certificate rule: ' + str(rule))
        active.remove(key)
        checked[key] = truth
        return truth

    visit(root)
    return len(checked)


def verify_4k4(c=None, prefix=None, params=None, prefix_data=None):
    folder = ROOT / 'data' / 'certificates'
    c = read_certificate('FINITE_CERTIFICATE.json.gz') if c is None else c
    prefix = read_certificate('PREFIX_CERTIFICATES.json.gz') if prefix is None else prefix
    params = strict_json((folder / 'PARAMETERS.json').read_text(encoding='utf-8')) if params is None else params
    prefix_data = strict_json((folder / 'PREFIX.json').read_text(encoding='utf-8')) if prefix_data is None else prefix_data
    a = from_lists(params['A_adjacency_lists'])
    n, s = len(a), params['base_level']
    require(n == 16 and s == 3, 'Wrong seed order or level')
    require(len(params['profile_vertex_sets']) == 3, 'The 4k+4 family has three auxiliary types')
    require(a == validate(c['A']), 'Seed and certificate adjacencies differ')
    b, _ = layers(a, params['profile_vertex_sets'], params['R_edges'], 1)
    require(b == validate(c['B']), 'Extension and certificate adjacencies differ')
    require(params['base_n'] == n and from_graph6(params['base_graph6']) == a, 'Encoded seed differs')
    require(from_graph6(params['B_graph6']) == b, 'Encoded extension differs')
    require(params['profiles'] == [sum(1 << v for v in p) for p in params['profile_vertex_sets']], 'Encoded profiles differ')
    type_pairs = list(combinations(range(3), 2))
    require(params['R_bits'] == sum(1 << i for i, e in enumerate(type_pairs) if list(e) in params['R_edges']), 'Encoded type graph differs')
    sizes = []
    for g, nodes, root, mask, level, truth in [
        (a, c['A_nodes'], c['A_positive_root'], (1 << n) - 1, s, True),
        (a, c['A_nodes'], c['A_negative_root'], (1 << n) - 1, s - 1, False),
        (b, c['B_nodes'], c['B_minus_p_positive_root'], ((1 << len(b)) - 1) ^ (1 << n), s, True),
    ]:
        sizes.append(check_nodes(g, nodes, root, mask, level, truth))
    rows = c['q_rows']
    require(len(rows) == len(b) - 1 and {r['v'] for r in rows} == set(range(len(b))) - {n}, 'Incomplete Euler table')
    for row in rows:
        require(type(row['v']) is int and type(row['q']) is int and all(type(x) is int and x >= 0 for x in row['coefficients']), 'Invalid clique row')
        co = coefficients(b, b[row['v']])
        require(co == enumerate_cliques(b, b[row['v']]), 'Independent clique counts disagree')
        padded = list(co) + [0] * (len(b) + 1 - len(co))
        require(padded == row['coefficients'], 'Incorrect clique coefficient')
        require(sum((-1) ** i * x for i, x in enumerate(co)) == row['q'] != 0, 'Incorrect Euler obstruction')
    require(params['q_rows'] == rows, 'Parameter and proof clique tables differ')
    subsets = []
    for k in ('1', '2'):
        z, p = prefix[k], prefix_data['levels'][k]
        subset = p['vertices_in_A16']
        g = validate(z['adjacency'])
        require(len(g) == 4 * int(k) + 4, 'Wrong prefix order')
        require(p['k'] == int(k) and p['n'] == len(g) and from_graph6(p['graph6']) == g, 'Encoded prefix differs')
        require(g == from_lists(p['adjacency_lists']) == induced(a, subset), 'Prefix is not the specified induced graph')
        subsets.append(set(subset))
        for key, level, truth in [('positive_root', int(k), True), ('negative_root', int(k) - 1, False)]:
            sizes.append(check_nodes(g, z['nodes'], z[key], (1 << len(g)) - 1, level, truth))
    require(subsets[0] < subsets[1] < set(range(n)), 'Prefixes are not nested')
    return {'roots': len(sizes), 'clique_rows': len(rows), 'reachable_nodes_per_root': sizes,
            'total_nodes': {'A': len(c['A_nodes']), 'B_minus_p': len(c['B_nodes'])},
            'claims': ['A in D_3', 'A outside D_2', 'B-p in D_3',
                       'H_1 in D_1 and outside D_0', 'H_2 in D_2 and outside D_1']}
