# Why the minimum at level two is twelve

Let $m_k$ be the least number of vertices in a graph of strict level $k$. The eight-vertex minimum $m_1=8$ is known. The graph $H_2$ supplies a twelve-vertex example at strict level two. To prove $m_2=12$, it remains to exclude graphs with at most eleven vertices.

Section 8 of the [supplement](../supplement/supplement.pdf) gives the complete reduction to the finite calculation. Choose a smallest induced subgraph $J$ of strict level two and the first vertex $v$ in a level-two reduction. Its neighbourhood graph $X$ has strict level one, and $v$ has at least one non-neighbour. If $U=V(J)\setminus N_J[v]$, the possible pairs $(|V(X)|,|U|)$ are $(8,1)$, $(9,1)$ and $(8,2)$.

The two cases with one non-neighbour are excluded by folds and a suspension argument. They are not delegated to a search. In the remaining case, the classification of small acyclic clique complexes places $X$ in one of seven eight-vertex isomorphism classes. The supplement supplies their missing edges, reductions and distinguishing invariants before describing the extensions.

## First check the seven graphs

```text
python reproduce.py --only small-orders
```

This verifies the seven reductions and pairwise non-isomorphism. It then checks all 13,599 entries in the supplied catalogues of graphs on zero through eight vertices, using augmented reduced homology over $\mathbb F_2$ and direct membership tests. Exactly seven classes are acyclic and outside $\mathcal D_0$; all seven lie in $\mathcal D_1$. Explicit isomorphisms link them to the displayed graphs and identify the class of $H_1$.

The empty graph has $\widetilde\beta_{-1}=1$ and lies in no dismantling class. The [catalogue guide](catalogues.md) describes the external sources and an additional completeness check that does not assume their class counts.

## Then check all remaining extensions

For each of the seven graphs, add $v$ adjacent to the eight old vertices, and two vertices $u_1,u_2$ not adjacent to $v$. Choose their neighbours $Z_1,Z_2$ among the old vertices and choose whether $u_1u_2$ is an edge. These choices specify every possible extension left by the proof.

```text
python reproduce.py --only order-eleven
```

The calculation considers $7\cdot2\cdot256^2=917,504$ ordered choices. Identifying the two orders by exchanging $u_1,u_2$ leaves 65,792 choices per graph, or 460,544 altogether. These numbers count extension choices, not isomorphism classes of eleven-vertex graphs.

For each extension the alternating clique sum $q$ is computed. If it is non-zero, the obstruction lemma excludes every dismantling level. If it is zero, the defining recursion tests levels zero, one and two. The recursion considers every first deletion needed to decide membership, including the reduction of the graph remaining after that deletion. Neither procedure imposes a search limit.

Two implementations classify every choice up to exchanging $u_1,u_2$. One uses integer adjacency rows and the clique-deletion recurrence; the other uses sets of vertices and a separate enumeration of cliques. They agree on every category and on $q$. The report checks all 28 expected counts and the identity between ordered, unordered and equal-subset counts. The separate `correspondence` group compares those expected counts with the displayed table. Any disagreement or strict-level-two extension stops the calculation with `FAIL`.

## Verify the twelve-vertex example

```text
python reproduce.py --only h2
```

The labels are those of the sixteen-vertex seed. The neighbourhood of vertex 7 is exactly $H_1$. Deleting 7 and following the recorded folds and neighbourhood reduction reaches a cone. The automorphism $(4\,5)(6\,7)(8\,9)(10\,11)(12\,13)$ reduces the initial level-one tests to seven representative vertices. Four of their neighbourhoods fold to the octahedral graph $K_{2,2,2}$; its non-zero alternating clique sum excludes ordinary dismantling. The other representatives have no dominated vertex. The report checks the automorphism, every recorded fold and these obstructions. This is an additional check of manuscript data; Section 4 already supplies complete recursive certificates for $H_1,H_2$ and the larger seed. Its reduction of $H_1$ differs from the equally valid reduction used here.

The finite exclusion and this example give $m_2=12$. The general descent inequality $m_k\geq m_{k-1}+2$ then gives $m_k\geq2k+8$ for $k\geq2$. The constructions provide the upper bound $\min\{4k+4,3k+8\}$; the exact values for $k\geq3$ are not determined. No enumeration of the minimisers on twelve vertices is asserted.
