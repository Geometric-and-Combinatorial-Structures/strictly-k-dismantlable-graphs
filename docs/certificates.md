# Finite certificates for the $4k+4$ family

To prove that a graph belongs to a dismantling class, it is enough to exhibit a reduction and justify every neighbourhood test. To prove non-membership, every possible first deletion must be excluded. The distributed certificates record both kinds of argument as finite collections of proof states.

## A state and its possible justifications

A state consists of a subset $S$ of the vertices of a fixed graph, an integer $j\geq-1$, and a Boolean assertion about whether the induced graph on $S$ belongs to $\mathcal D_j$. There are five rules:

| Rule | Required justification |
| --- | --- |
| Empty graph | $S=\varnothing$; membership is false at every level. |
| Cone | A specified vertex is an apex of the non-empty induced graph; membership is true at every level. |
| Non-cone at level $-1$ | The graph is non-empty and has no apex; membership is false. |
| Positive deletion | For a vertex $v\in S$, the neighbourhood state $(S\cap N(v),j-1)$ and remainder state $(S\setminus\lbrace v\rbrace,j)$ are both true. |
| Negative state | For every $v\in S$, at least one of those two states is false. The graph is non-empty, is not a cone, and $j\geq0$. |

Every child has fewer vertices. The verifier checks this decrease, the exact subset and level of each child, every reference to another state, and complete coverage of the vertices in a negative state. It rejects self-referential dependencies and incorrect truth values. Induction on $|S|$, using the definition of the hierarchy, proves that each accepted state has the asserted meaning.

## The seven roots

Here $A$ is the sixteen-vertex seed and $B$ is its first layer extension; $p$ is the added centre, whose neighbourhood is $A$.

The three main roots assert $A\in\mathcal D_3$, $A\notin\mathcal D_2$, and $B-p\in\mathcal D_3$. The four prefix roots assert $H_1\in\mathcal D_1$, $H_1\notin\mathcal D_0$, $H_2\in\mathcal D_2$, and $H_2\notin\mathcal D_1$. Each root is bound to the complete claimed vertex set and level; the prefix graphs are also checked as the specified induced subgraphs of $A$.

The files in [`data/certificates`](../data/certificates) contain:

| File | Mathematical contents |
| --- | --- |
| `PARAMETERS.json` | The sixteen-vertex seed, its base level, profiles and type graph. |
| `PREFIX.json` | The two ordered prefix vertex sets and their induced adjacency lists. |
| `FINITE_CERTIFICATE.json.gz` | The seed and extension proof states, their three roots and all nineteen clique rows. |
| `PREFIX_CERTIFICATES.json.gz` | The prefix proof states and their four roots. |

The `.gz` files are compressed JSON text; Python reads them directly. Each subset is encoded by an integer $m=\sum_{v\in S}2^v$. A node records this integer as `m`, the level as `k`, its truth value as `value`, and its justification as `rule`. The key `link` refers to the neighbourhood state and `rest` to the state after deleting the chosen vertex. In a negative state, `child` refers to the failed condition specified by `side`, which is either `link` or `rest`. In a prefix certificate, a bit position indexes the ordered list `vertices_in_A16`, rather than the original seed label. The graph6 strings and all duplicate encodings in the data are decoded and compared as well. Vertex labels in the seed are $0,\ldots,15$; the centre is $16$ and the auxiliaries are $17,18,19$.

The verifier [`dismantling/certificates.py`](../dismantling/certificates.py) checks the supplied proof states without searching for a dismantling order. A separate exact recursion recomputes all seven membership assertions directly from the definition, without using the stored proof states. The seven accepted roots are therefore complete finite proofs, not conclusions drawn from an unsuccessful bounded search.

Run `python reproduce.py --only 4k4` to verify the certificates. Run `python reproduce.py --only mutations` to check rejection of altered edges, root levels and subsets, missing branches, missing or self-referential dependencies, and incorrect clique coefficients.
