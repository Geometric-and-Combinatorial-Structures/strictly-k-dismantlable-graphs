#!/usr/bin/env python3
"""Construct a member of one of the three families at a specified strict level."""
import sys
sys.dont_write_bytecode = True
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or later is required.')
import argparse
import tempfile
_bytecode_directory = tempfile.TemporaryDirectory(prefix='strict-dismantling-bytecode-')
sys.pycache_prefix = _bytecode_directory.name
from dismantling.graphs import family_graph, edges, vertices
from dismantling.output import new_directory, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', required=True, choices=['3k8', '4k4', '6k6'])
    parser.add_argument('--k', required=True, type=int, help='Strict dismantling level, at least 1.')
    parser.add_argument('--output', help='A new output directory.')
    args = parser.parse_args(argv)
    if args.k < 1:
        parser.error('k must be at least 1')
    g, labels = family_graph(args.family, args.k)
    try:
        output = new_directory(args.output, args.family + '-k' + str(args.k))
    except ValueError as exc:
        parser.error(str(exc))
    es = edges(g)
    result = {'family': args.family, 'k': args.k, 'vertices': len(g), 'edges': es,
              'labels': labels, 'adjacency': [list(vertices(ns)) for ns in g]}
    write_json(output / 'graph.json', result)
    (output / 'edges.txt').write_text(''.join(f'{u} {v}\n' for u, v in es), encoding='utf-8')
    rows = [f'Family {args.family}, strict level {args.k}', f'{len(g)} vertices and {len(es)} edges.', '',
            'The integers in edges.txt refer to the following vertex labels:']
    rows += [f'{i}: ' + ('a_' + str(v[1]) if v[0] == 'a' else 'c_' + str(v[1]) if v[0] == 'c' else f'x_{{{v[1]},{v[2]}}}') for i, v in enumerate(labels)]
    rows += ['', 'The stated strict level follows from the construction theorem and its verified seed hypotheses.',
             'This command constructs the graph; it does not search for a dismantling order.', '']
    (output / 'description.txt').write_text('\n'.join(rows), encoding='utf-8')
    print(f'{len(g)} vertices, {len(es)} edges. Files: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
