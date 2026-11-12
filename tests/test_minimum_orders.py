"""Independent decisions, malformed witnesses and catalogue boundaries."""
import copy
import unittest
from unittest.mock import patch
from dismantling.graphs import from_edges, family_graph, validate
from dismantling.order_eleven import MISSING, seed, extend, classify, crosscheck
from dismantling.small_orders import CERTIFICATES, printed_certificates, isomorphism
from dismantling.reference import classify as reference_classify
from dismantling.catalogues import unlabelled_count
from dismantling import correspondence


class MinimumOrderTests(unittest.TestCase):
    def test_extension_has_exactly_the_prescribed_edges(self):
        for missing in MISSING:
            base=seed(missing)
            for s in (0,1,85,255):
                for t in (0,128,170,255):
                    for edge in (False,True):
                        graph=extend(base,s,t,edge)
                        validate(graph)
                        self.assertEqual(graph[8],255)
                        self.assertEqual(graph[9],s | (int(edge)<<10))
                        self.assertEqual(graph[10],t | (int(edge)<<9))
                        self.assertEqual([row & 255 for row in graph[:8]],base)
                        self.assertEqual(sum(row.bit_count() for row in graph)//2,
                                         sum(row.bit_count() for row in base)//2+8+s.bit_count()+t.bit_count()+edge)

    def test_boundary_and_strict_two_decisions(self):
        for g,wanted in [((), 'nonzero_q'),((0,), 'D0'),
                         (tuple(seed(MISSING[0])), 'strict1')]:
            self.assertEqual(classify(g),wanted)
            self.assertEqual(reference_classify(g)[0],wanted)
            crosscheck(g,wanted)
        h2,_ = family_graph('4k4',2)
        self.assertEqual(reference_classify(h2)[0],'strict2')
        with self.assertRaises(AssertionError):
            classify(h2)

    def test_false_category_is_rejected(self):
        g=tuple(seed(MISSING[0]))
        with self.assertRaises(ValueError):
            crosscheck(g,'D0')
        with self.assertRaises(ValueError):
            crosscheck(g,'zero_q_outside_D2')

    def test_altered_seed_certificate_is_rejected(self):
        graphs=[seed(m) for m in MISSING]
        bad=copy.deepcopy(CERTIFICATES)
        first,path,folds,apex=bad[0]
        path[0]=first
        with patch('dismantling.small_orders.CERTIFICATES',bad):
            with self.assertRaises(AssertionError):
                printed_certificates(graphs)
        with self.assertRaises(ValueError):
            seed(MISSING[0]+[MISSING[0][0]])

    def test_isomorphism_includes_edges_and_non_edges(self):
        path=from_edges(4,[(0,1),(1,2),(2,3)])
        relabelled=from_edges(4,[(0,2),(0,3),(1,3)])
        star=from_edges(4,[(0,1),(0,2),(0,3)])
        self.assertIsNotNone(isomorphism(path,relabelled))
        self.assertIsNone(isomorphism(path,star))
        self.assertEqual(isomorphism((),()),{})

    def test_burnside_initial_orders(self):
        self.assertEqual([unlabelled_count(n) for n in range(5)],[1,1,2,4,11])

    def test_changed_printed_count_is_rejected(self):
        original=correspondence.rows
        def altered(name):
            rows=original(name)
            if name=='small_extensions.tex':
                rows[0][1]=str(int(rows[0][1])+1)
            return rows
        with patch('dismantling.correspondence.rows',side_effect=altered):
            with self.assertRaises(ValueError):
                correspondence.run()


if __name__=='__main__':
    unittest.main()
