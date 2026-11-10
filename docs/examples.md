# Constructing a graph at a chosen level

The construction adds layers to a seed while retaining all previous adjacencies. A layer contains one centre and a fixed number of auxiliary vertices. The neighbours of a centre induce the preceding graph, which is the step that raises the strict dismantling level.

| Family in the mathematics | `generate.py --family` | `reproduce.py --only` | Order at level $k$ | Starting graphs |
| --- | --- | --- | --- | --- |
| $F_k$ | `3k8` | `article` | $3k+8$ | An eleven-vertex seed at level one; two auxiliaries per layer. |
| $H_k$ | `4k4` | `4k4` | $4k+4$ | Prefixes at levels one and two, followed by a sixteen-vertex seed at level three; three auxiliaries per layer. |
| $J_k$ | `6k6` | `6k6` | $6k+6$ | A twelve-vertex seed at level one; five auxiliaries per layer. |

All three commands accept any integer $k\geq1$, subject to the memory available for the resulting graph. For instance:

```text
python generate.py --family 3k8 --k 5
```

This constructs $F_5$, with **23 vertices and 215 edges**, and saves three files in a new directory beneath `results/`:

| File | How to read it |
| --- | --- |
| `description.txt` | The family, level, order, size, and correspondence between numerical labels and the mathematical vertex names. |
| `edges.txt` | One unordered edge per line, given by its two numerical endpoint labels. |
| `graph.json` | The full edge list, adjacency list and original vertex labels in a structured text file. |

The mathematical labels distinguish seed vertices `a_i`, centres `c_i`, and auxiliary vertices `x_{j,i}` of type $j$ in layer $i$. For the two prefixes of $H_k$, the seed labels are retained even though the file's numerical indices start at zero. The correspondence in `description.txt` makes this relabelling explicit.

To obtain the first three members of $H_k$, run the command separately with `--k 1`, `--k 2` and `--k 3`. Their orders are eight, twelve and sixteen. The first two are induced subgraphs of the third, as proved in the supplement.

The generator applies the adjacency definition. The assertion about the strict level follows from the verified seed hypotheses and the construction theorem; generating a graph does not perform a new search for its dismantling level. Use `python reproduce.py` to verify those finite hypotheses.
