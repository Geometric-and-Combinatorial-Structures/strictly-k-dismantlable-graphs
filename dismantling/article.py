"""Independently check the article tables and the incidences drawn in its figures."""

if not __debug__:
    raise SystemExit("Run verification without -O or -OO.")

def run():
    import datetime
    import hashlib
    import itertools
    from .graphs import strict_json
    import re
    from pathlib import Path
    
    ROOT = Path(__file__).resolve().parents[1]
    INPUTS = [
        'data/article_remainder.json', 'data/family_3k8.json',
        'data/article_tables/seed_adjacency.tex', 'data/article_tables/seed_reduction.tex',
        'data/article_tables/seed_cliques.tex', 'figures/seed_complement.tikz',
        'figures/layers.tikz', 'figures/first_layer.tikz',
        'figures/layers_scheme.tex',
    ]
    RAW = {p: (ROOT / p).read_bytes() for p in INPUTS}
    TXT = {p: b.decode('utf-8') for p, b in RAW.items()}
    
    
    def pair(a, b):
        assert a != b
        return tuple(sorted((a, b)))
    
    
    def edges_of(adj):
        return {pair(v, w) for v, ns in adj.items() for w in ns}
    
    
    def graph(vertices, edges):
        adj = {v: set() for v in vertices}
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
        return adj
    
    
    def induced(adj, vertices):
        vertices = set(vertices)
        return {v: adj[v] & vertices for v in vertices}
    
    
    def folds(adj):
        return sorted((u, v) for u in adj for v in adj
                      if u != v and adj[u] | {u} <= adj[v] | {v})
    
    
    def do_fold(adj, u, v):
        assert u != v and u in adj and v in adj
        assert adj[u] | {u} <= adj[v] | {v}, (u, v)
        return induced(adj, set(adj) - {u})
    
    
    def figure(name):
        text = TXT['figures/' + name]
        lines = [s for s in text.splitlines() if s.startswith('\\draw')]
        es = []
        for line in lines:
            endpoints = re.findall(r'\(([a-z]+\d*)\)', line)
            assert len(endpoints) == 2, line
            es.append(pair(*endpoints))
        assert len(es) == len(set(es)), 'Duplicate emitted edge'
        labels = re.findall(r'\\node[^\n]*? at \((\w+)\) \{\$(.*?)\$\};', text)
        assert len(labels) == text.count('\\node'), 'Non-mathematical/unparsed node label'
        nodes = dict(labels)
        assert len(nodes) == len(labels), 'Duplicate emitted node'
        coords = re.findall(r'\\coordinate \((\w+)\)', text)
        assert set(coords) == set(nodes) and len(coords) == len(nodes)
        assert all(a in nodes and b in nodes for a, b in es)
        assert text.rfind('\\draw') < text.find('\\node'), 'Edges must precede nodes'
        return nodes, set(es)
    
    
    adj_text = TXT['data/article_tables/seed_adjacency.tex']
    matches = re.findall(r'^\$(\d+)\$\s*&\s*\$\\\{([0-9,]+)\\\}\$', adj_text, re.M)
    assert len(matches) == 11
    A = {v: set(ns.split(',')) for v, ns in matches}
    assert set(A) == {str(i) for i in range(11)}
    assert all(v not in ns and ns <= set(A) for v, ns in A.items())
    assert all(v in A[w] for v, ns in A.items() for w in ns)
    EA = edges_of(A)
    assert len(EA) == 33
    family_data = strict_json(TXT['data/family_3k8.json'])
    assert family_data['family'] == '3k8' and family_data['n'] == 11 and family_data['s'] == 1
    assert family_data['A'] == [sorted(map(int, A[str(v)])) for v in range(11)]
    assert family_data['profiles'] == [[v for v in range(11) if v != 2], [v for v in range(11) if v != 1]]
    assert family_data['R'] == [[0, 1]]
    
    # Parse each reduction row from the emitted table, not from a copied witness.
    reduction_rows = []
    outer_graph = A
    inner_count = 0
    for line in TXT['data/article_tables/seed_reduction.tex'].splitlines():
        if not re.match(r'^\$\d+\$&', line):
            continue
        fields = line.split('&')
        v = re.fullmatch(r'\$(\d+)\$', fields[0]).group(1)
        ns = set(re.search(r'\\\{([0-9,]+)\\\}', fields[1]).group(1).split(','))
        witness = re.findall(r'(\d+)\\to(\d+)', fields[2])
        survivor = re.search(r'\$(\d+)\$', fields[3]).group(1)
        assert v in outer_graph and outer_graph[v] == ns
        inner_graph = induced(outer_graph, ns)
        for u, target in witness:
            inner_graph = do_fold(inner_graph, u, target)
        assert set(inner_graph) == {survivor}
        inner_count += len(witness)
        reduction_rows.append({'deleted': v, 'current_neighbours': sorted(ns),
                               'folds': witness, 'survivor': survivor})
        outer_graph = induced(outer_graph, set(outer_graph) - {v})
    assert len(reduction_rows) == 10 and inner_count == 23 and set(outer_graph) == {'10'}
    assert [r['deleted'] for r in reduction_rows] == ['5','2','1','4','0','6','7','8','9','3']
    
    
    forced = [folds(A), folds(induced(A, set(A)-{'5'})),
              folds(induced(A, set(A)-{'5','9'}))]
    assert forced == [[('5','2')], [('9','7')], []]
    
    # Expand exactly the stated first-layer profiles: p sees A, x omits 2,
    # y omits 1, and xy is present. Neither px nor py is present.
    new_edges = {pair('p', a) for a in A}
    new_edges |= {pair('x', a) for a in A if a != '2'}
    new_edges |= {pair('y', a) for a in A if a != '1'}
    new_edges.add(pair('x', 'y'))
    B = graph(set(A) | {'p', 'x', 'y'}, EA | new_edges)
    assert len(new_edges) == 32 and len(edges_of(B)) == 65
    rest_folds = strict_json(TXT['data/article_remainder.json'])['folds']
    rest = induced(B, set(B)-{'p'})
    for u, target in rest_folds:
        rest = do_fold(rest, u, target)
    assert len(rest_folds) == 12 and set(rest) == {'y'}
    
    clique_rows = []
    for line in TXT['data/article_tables/seed_cliques.tex'].splitlines():
        if not re.match(r'^\$(\d+|x|y)\$&', line):
            continue
        fields = line.split('&')
        v = fields[0].strip('$')
        expected = [int(x) for x in fields[1:6]]
        q_expected = int(re.search(r'-?\d+', fields[6]).group())
        H = induced(B, B[v])
        counts = [sum(all(b in H[a] for a,b in itertools.combinations(C,2))
                      for C in itertools.combinations(sorted(H), t))
                  for t in range(len(H)+1)]
        assert counts[:5] == expected and not any(counts[5:]), v
        q_actual = sum((-1)**t*n for t,n in enumerate(counts))
        assert q_actual == q_expected != 0
        clique_rows.append({'vertex': v, 'counts': counts, 'q': q_actual,
                            'max_clique_cardinality': max(t for t,n in enumerate(counts) if n)})
    assert len(clique_rows) == 13 and {r['vertex'] for r in clique_rows} == set(B)-{'p'}
    
    # The seed-origin check is only an edge-set identity, not a validation of
    # the historical kernel catalogue, kernel acyclicity or discovery history.
    assert pair('1','2') in EA
    kernel_edges = EA - {pair('1','2')}
    assert len(kernel_edges) == 32 and kernel_edges | {pair('1','2')} == EA
    
    seed_nodes, seed_edges = figure('seed_complement.tikz')
    assert seed_nodes == {'v'+v: v for v in A}
    all_pairs = {pair(a,b) for a,b in itertools.combinations(A,2)}
    expected_complement = {pair('v'+a,'v'+b) for a,b in all_pairs-EA}
    assert seed_edges == expected_complement and len(seed_edges) == 22
    assert not ((all_pairs-EA) & EA) and (all_pairs-EA) | EA == all_pairs
    
    layer_nodes, layer_edges = figure('layers.tikz')
    roles = {}
    for node, label in layer_nodes.items():
        c = re.fullmatch(r'c_\{(\d+)\}', label)
        x = re.fullmatch(r'x_\{(\d+),(\d+)\}', label)
        assert bool(c) != bool(x), label
        roles[node] = ('c', int(c[1])) if c else ('x', int(x[1]), int(x[2]))
    assert set(roles.values()) == {('c', i) for i in range(3)} | {('x', j, i) for j in range(2) for i in range(3)}
    expected_layer_edges = set()
    for a,b in itertools.combinations(roles,2):
        u,v = roles[a],roles[b]
        allowed = u[0] == v[0]  # all centres; all auxiliaries because R=K2
        if u[0] != v[0]:
            c,x = (u,v) if u[0] == 'c' else (v,u)
            allowed = c[1] != x[2]
        if allowed:
            expected_layer_edges.add(pair(a,b))
    assert layer_edges == expected_layer_edges and len(layer_edges) == 30
    
    first_nodes, first_edges = figure('first_layer.tikz')
    assert first_nodes == {'w':'W', 'a':'1', 'b':'2', 'p':'p', 'x':'x', 'y':'y'}
    blocks = {'w':set(A)-{'1','2'}, 'a':{'1'}, 'b':{'2'},
              'p':{'p'}, 'x':{'x'}, 'y':{'y'}}
    expanded = [pair(u,v) for a,b in first_edges for u in blocks[a] for v in blocks[b]]
    assert len(first_edges) == 8 and len(expanded) == len(set(expanded)) == 32
    assert set(expanded) == new_edges
    
    # Refuse a report over files that changed during this check.
    assert all((ROOT/p).read_bytes() == b for p,b in RAW.items())
    report = {
        'status': 'PASS', 'method': 'Independent adjacency-set verification of the article data and figures',
        'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Displayed finite reductions, clique tables and exact figure incidences.',
        'inputs': [{'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for p,b in RAW.items()],
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'seed': {'vertices':len(A),'edges':len(EA),'reciprocal_adjacency':True},
        'D1_reduction': {'outer_deletions':len(reduction_rows),'inner_folds':inner_count,'rows':reduction_rows,'last_vertex':'10'},
        'D0_exclusion': {'all_folds_at_three_stages':forced,'remaining_vertices':9},
        'extension': {'vertices':len(B),'edges':len(edges_of(B)),'added_edges':len(new_edges)},
        'remainder': {'folds':rest_folds,'fold_count':len(rest_folds),'last_vertex':'y'},
        'clique_counts': {'rows':clique_rows,'rows_checked':len(clique_rows),'no_cliques_above_four':True},
        'kernel_identity_only': {'removed_edge':['1','2'],'edges_after_removal':32,'restoring_edge_returns_A':True,
                                 'not_evaluated':'Kernel catalogue, homology, provenance of discovery'},
        'figures': {'seed_complement':{'vertices':11,'edges':22,'exact_edge_set':True},
                    'layers':{'vertices':9,'edges':30,'exact_induced_new_vertex_edge_set':True,'d':2,'m':3,'R':'K2'},
                    'first_layer':{'emitted_incidences':8,'expanded_distinct_edges':32,'exact_added_edge_set':True},
                    'all_labels_in_math_mode':True,'node_labels_match_roles':True,'edges_before_nodes':True},
    }
    return report
