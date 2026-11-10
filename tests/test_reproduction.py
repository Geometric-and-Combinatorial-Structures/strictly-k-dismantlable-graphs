"""Boundary and negative tests for the public entry points and mathematical verifier."""
import sys
sys.dont_write_bytecode = True
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from dismantling.graphs import ROOT, from_lists, from_edges, family_graph
from dismantling.certificates import check_nodes
from dismantling.output import new_directory


class VerificationTests(unittest.TestCase):
    def test_graph_validation_rejects_bad_inputs(self):
        for data in ([[0]], [[1], []], [[1, 1], [0]], [[2], [0]], [[True], [0]]):
            with self.assertRaises(ValueError):
                from_lists(data)
        with self.assertRaises(ValueError):
            from_edges(2, [(0, 1), (0, 1)])

    def test_empty_and_cone_certificates(self):
        empty = {'e': {'m': 0, 'k': 2, 'value': False, 'rule': 'empty'}}
        self.assertEqual(check_nodes((), empty, 'e', 0, 2, False), 1)
        cone = {'c': {'m': 1, 'k': -1, 'value': True, 'rule': 'cone', 'apex': 0}}
        self.assertEqual(check_nodes((0,), cone, 'c', 1, -1, True), 1)
        cone['c']['value'] = 1
        with self.assertRaises(ValueError):
            check_nodes((0,), cone, 'c', 1, -1, True)

    def test_wrong_child_and_cycle_are_rejected(self):
        g = from_edges(2, [(0, 1)])
        root = {'m': 3, 'k': 0, 'value': True, 'rule': 'delete', 'vertex': 0, 'link': 'q', 'rest': 'q'}
        nodes = {'r': root, 'q': {'m': 2, 'k': 0, 'value': True, 'rule': 'cone', 'apex': 1}}
        with self.assertRaises(ValueError):
            check_nodes(g, nodes, 'r', 3, 0, True)
        root['link'] = 'r'
        with self.assertRaises(ValueError):
            check_nodes(g, nodes, 'r', 3, 0, True)

    def test_invalid_levels(self):
        for k in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                family_graph('3k8', k)

    def test_output_preserves_prior_results(self):
        with tempfile.TemporaryDirectory() as parent:
            path = new_directory(Path(parent) / 'new')
            sentinel = path / 'keep.txt'
            sentinel.write_text('earlier result')
            with self.assertRaises(ValueError):
                new_directory(path)
            self.assertEqual(sentinel.read_text(), 'earlier result')
        with self.assertRaises(ValueError):
            new_directory(ROOT / 'data' / 'unwanted-output')

    def test_generation_from_another_directory(self):
        with tempfile.TemporaryDirectory() as parent:
            out = Path(parent) / 'new graph'
            process = subprocess.run([sys.executable, str(ROOT / 'generate.py'), '--family', '3k8', '--k', '5', '--output', str(out)],
                                     cwd=parent, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            graph = json.loads((out / 'graph.json').read_text())
            self.assertEqual((graph['vertices'], len(graph['edges'])), (23, 215))
            repeated = subprocess.run([sys.executable, str(ROOT / 'generate.py'), '--family', '3k8', '--k', '5', '--output', str(out)],
                                      cwd=parent, capture_output=True)
            self.assertNotEqual(repeated.returncode, 0)

    def test_optimised_verification_is_refused(self):
        result = subprocess.run([sys.executable, '-O', str(ROOT / 'reproduce.py')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('without -O', result.stderr)


if __name__ == '__main__':
    unittest.main()
