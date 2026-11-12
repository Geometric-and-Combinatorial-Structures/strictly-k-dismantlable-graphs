# External graph catalogues

The graph catalogues in `data/catalogues/` are external mathematical data. They are excluded from the authors' CC BY 4.0 grant; inclusion here does not assert ownership or impose a new licence on them.

- `graph7.g6` and `graph8.g6` come from [Brendan D. McKay's collection](https://users.cecs.anu.edu.au/~bdm/data/graphs.html), with 1,044 and 12,346 graphs. The distributed bytes were compared with fresh downloads from the source on 12 November 2026.
- `graphs0to6.g6` contains 209 graphs exported from NetworkX 3.7's [`graph_atlas_g()`](https://networkx.org/documentation/stable/reference/generated/networkx.generators.atlas.graph_atlas_g.html), restricted to orders at most six. The atlas follows R. C. Read and R. J. Wilson, *An Atlas of Graphs*, Oxford University Press, 1998. NetworkX software is distributed under BSD-3-Clause; no NetworkX code is included or required to run the calculations.

[The provenance record](data/catalogues/provenance.json) gives source addresses, SHA-256 sums and the exact export expression. [The catalogue guide](docs/catalogues.md) explains how completeness is checked independently.
