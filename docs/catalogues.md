# The small-graph catalogues

The small-order check uses one representative of each simple graph of order zero through eight. Their counts by order are

| Order | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphs | 1 | 1 | 2 | 4 | 11 | 34 | 156 | 1,044 | 12,346 |

The entries are encoded in [graph6 format](https://users.cecs.anu.edu.au/~bdm/data/formats.txt). The public inputs retain the original catalogue order and are identified by their source and SHA-256 in [provenance.json](../data/catalogues/provenance.json). [THIRD_PARTY.md](../THIRD_PARTY.md) records their attribution. NetworkX is not a runtime dependency; it was used only to export the file for orders at most six.

The default calculation checks the file identities, orders, distinct encodings and each graph's homology and dismantling levels. The main command also establishes completeness up to isomorphism. To run that group alone:

```text
python reproduce.py --only catalogue-completeness
```

First, exact isomorphism tests show that no two entries represent the same graph. Isomorphism invariants group the comparisons; graphs in different groups cannot be isomorphic. Within a group, the search considers every degree-compatible bijection and checks both edges and non-edges.

Second, the program derives the total number of classes from Burnside's lemma. A permutation $\pi$ of the $n$ vertices acts on the unordered vertex pairs. If this action has $o(\pi)$ orbits, exactly $2^{o(\pi)}$ edge sets are fixed by $\pi$. Hence the number of unlabelled simple graphs is

$$\frac{1}{n!}\sum_{\pi\in S_n}2^{o(\pi)}.$$

All permutations are considered for each $0\leq n\leq8$. The resulting counts agree with the table and with the pairwise non-isomorphic catalogue entries. Thus no class is missing. This validates the finite input collection; the separate homology and membership calculations establish the classification used in the minimum-order argument.
