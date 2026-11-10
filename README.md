# Graphs at every strict dismantling level

How many vertices are needed for a graph that can be dismantled at level $k$, but not at level $k-1$?

An ordinary dismantling repeatedly **folds** a vertex onto a neighbour whose closed neighbourhood contains its own. At a higher level, the deletion is allowed when the graph induced by its current neighbours can be dismantled at the preceding level. This repository accompanies **[Linear-size graphs at every strict dismantling level](ARTICLE.md)** and supplies the supplementary proofs, explicit graphs and finite verifications for its constructions.

The article gives two families, $F_k$ and $H_k$, of strict level $k$ for every $k\geq1$, with $3k+8$ and $4k+4$ vertices, respectively. Hence the least order at strict level $k$ is **at most** $\min\{4k+4,3k+8\}$. A third family, $J_k$, developed in the supplement, has $6k+6$ vertices. Each family is obtained from a finite seed by adding a fixed number of vertices per layer.

## Begin with a small example

The first member $H_1$ has eight vertices. Two deletions reduce it to a **cone**, a graph with a vertex adjacent to every other vertex. Each deletion is justified by a single fold inside the relevant neighbourhood. Yet none of its original neighbourhoods is a cone, so an ordinary dismantling cannot begin. The supplement gives the complete adjacency list and this short proof before introducing the larger certificates.

To construct the example, run:

```text
python generate.py --family 4k4 --k 1
```

The command writes its adjacency list, edge list and vertex labels to a new directory beneath `results/`. The proof and all the other required finite calculations can then be checked with:

```text
python reproduce.py
```

Python 3.11 or later is sufficient; the calculations use its standard library. The [reproduction guide](docs/reproduction.md) explains how to obtain the files, run these commands and read the results. You can also [open the guided notebook in Google Colab](https://colab.research.google.com/github/Geometric-and-Combinatorial-Structures/strictly-k-dismantlable-graphs/blob/v1.0.0/notebooks/reproduce.ipynb) and run the same calculations in a browser.

## Choose a route

| Your purpose | Where to begin |
| --- | --- |
| **Read the proofs** | [Mathematical supplement (PDF)](supplement/supplement.pdf): the two supplementary families, kernel completion and the homological extension, with shared notation and linked results. [LaTeX sources](supplement/main.tex) are included. |
| **Reproduce the calculations** | [Reproduction guide](docs/reproduction.md), followed by the [result-by-result correspondence](docs/results.md). Every calculation is linked to its mathematical purpose and expected output. |
| **Construct examples** | [Guide to the three families](docs/examples.md): choose a family and a level, then obtain the graph with its original seed and layer labels. |

The supplement develops four related parts. The $4k+4$ family supplies the finite evidence used in §7 of the article. The $6k+6$ family gives another complete application of the same construction. Kernel completion explains how adding one edge produces the eleven-vertex seed of $F_k$. The homological extension then follows the neighbourhood obstructions through all subsequent layers, using reduced homology over $\mathbb F_2$.

## What the calculations establish

The main command verifies the article's seed reductions, clique tables and figure incidences; all seven recursive proof roots and nineteen clique rows for $H_k$; the complete finite witnesses for the $6k+6$ family; and the kernel and homology calculations. It also compares two independent implementations of the six adjacency rules, compares two methods of counting cliques, and checks that deliberately altered certificates are rejected.

To check the additional finite ranges, run:

```text
python reproduce.py --extended
```

The extended calculation additionally checks all small constructions in the ranges stated in the guide. These finite checks support the explicit data and identities. The proofs in the supplement establish the conclusions for **every** level. The minimum cost of three vertices per layer concerns the construction under its Euler hypotheses, including the non-zero alternating clique sums in all non-central neighbourhoods. The single-deletion check verifies a separate result: for $F_k$ with $k\geq2$, deleting a centre leaves an ordinarily dismantlable graph, whereas deleting any other vertex gives a graph outside every dismantling class. This concerns **one vertex at a time**; Appendix A gives the proof.

Each run creates a new directory containing a readable `report.txt` and a detailed `report.json`. Earlier results and the distributed inputs are preserved. A failed or interrupted calculation is reported as such; it is never counted as a successful check.

## Citation and licences

Use [ARTICLE.md](ARTICLE.md) for the authors and article reference, and cite this repository's release `v1.0.0` when referring to its data or calculations. [CITATION.cff](CITATION.cff) supplies the repository citation. The code is distributed under the [MIT licence](LICENSE-MIT.txt); the authors' documentation, data, figures and supplement are distributed under [CC BY 4.0](LICENSE-DATA-DOCS.md).

[SHA256SUMS.txt](SHA256SUMS.txt) records the checksum of every distributed file. The reproduction command checks these sums before beginning the mathematical calculations.
