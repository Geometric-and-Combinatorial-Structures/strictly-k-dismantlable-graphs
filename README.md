# Graphs at every strict dismantling level

How many vertices are needed for a graph that can be dismantled at level $k$, but not at level $k-1$?

An ordinary dismantling repeatedly **folds** a vertex onto a neighbour whose closed neighbourhood contains its own. At a higher level, the deletion is allowed when the graph induced by its current neighbours can be dismantled at the preceding level. This repository accompanies **[Linear-size graphs at every strict dismantling level](ARTICLE.md)** and supplies the supplementary proofs, explicit graphs and finite verifications for its constructions.

The article gives two families, $F_k$ and $H_k$, of strict level $k$ for every $k\geq1$, with $3k+8$ and $4k+4$ vertices, respectively. Writing $m_k$ for the least order at strict level $k$, these constructions give the **upper bound** $m_k\leq\min\lbrace 4k+4,3k+8\rbrace$. The supplement develops a third family, $J_k$, with $6k+6$ vertices. Each family grows from a finite seed by adding a fixed number of vertices per layer.

The supplement also gives the argument and finite verification establishing $m_2=12$. The descent inequality then yields $m_k\geq2k+8$ for $k\geq2$. The [minimum-order guide](docs/minimum-orders.md) explains why the proof reduces to a specified collection of eleven-vertex extensions and how to reproduce that calculation.

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

Python 3.11 or later is sufficient; the calculations use its standard library. The [reproduction guide](docs/reproduction.md) explains how to obtain the files, run these commands and read the results. You can also [open the guided notebook in Google Colab](https://colab.research.google.com/github/Geometric-and-Combinatorial-Structures/strictly-k-dismantlable-graphs/blob/v1.1.0/notebooks/reproduce.ipynb) and run the same calculations in a browser.

## Choose a route

| Your purpose | Where to begin |
| --- | --- |
| **Read the proofs** | [Mathematical supplement (PDF)](supplement/supplement.pdf): the families of orders $4k+4$ and $6k+6$, kernel completion, the homological extension and the minimum at level two, together with the finite data for $F_k$, using shared notation and linked results. [LaTeX sources](supplement/main.tex) are included. |
| **Reproduce the calculations** | [Reproduction guide](docs/reproduction.md), followed by the [result-by-result correspondence](docs/results.md). Every calculation is linked to its mathematical purpose and expected output. |
| **Construct examples** | [Guide to the three families](docs/examples.md): choose a family and a level, then obtain the graph with its original seed and layer labels. |

The supplement develops four related parts. The $4k+4$ family supplies the finite evidence used in §7 of the article. The $6k+6$ family gives another complete application of the same construction. Kernel completion explains how adding one edge produces the eleven-vertex seed of $F_k$. The homological extension then follows the neighbourhood obstructions through all subsequent layers, using reduced homology over $\mathbb F_2$.

## What the calculations establish

The main command verifies the seed reductions, clique tables and figure incidences; all seven recursive proof roots and nineteen clique rows for $H_k$; the finite witnesses for $J_k$; and the kernel and homology calculations. Direct recursive tests check the strict levels of $F_k$ and $H_k$ for $1\leq k\leq7$.

For the minimum at level two, it checks the seven eight-vertex graphs, the twelve-vertex witness, and all 460,544 extension choices left by the case reduction. Two separately implemented decision procedures must agree on every choice. Further controls compare independent adjacency constructions and clique counts, and require deliberately altered certificates to be rejected.

To check the additional finite ranges, run:

```text
python reproduce.py --extended
```

The main calculation establishes completeness of the small-graph catalogues by exact isomorphism tests and Burnside counts. The extended calculation adds the finite ranges stated in the guide. The finite tests support the explicit data; the construction proofs establish the strict levels for **every** $k$. The minimum of three new vertices per layer concerns the stated template under its Euler hypotheses.

The article also proves a dichotomy for deleting **one vertex** from $F_k$, for $k\geq2$. A centre deletion leaves an ordinarily dismantlable graph; any other deletion leaves a graph outside every dismantling class. The corresponding calculation checks all single deletions at $k=2,3,4$.

Each run creates a new directory containing a readable `report.txt` and a detailed `report.json`. Earlier results and the distributed inputs are preserved. A failed or interrupted calculation is reported as such; it is never counted as a successful check.

## Citation and licences

Use [ARTICLE.md](ARTICLE.md) for the authors and article reference, and cite [release `v1.1.0` (DOI 10.5281/zenodo.24157746)](https://doi.org/10.5281/zenodo.24157746) when referring to its data or calculations. [CITATION.cff](CITATION.cff) supplies the repository citation. The code is distributed under the [MIT licence](LICENSE-MIT.txt); the authors' documentation, data, figures and supplement are distributed under [CC BY 4.0](LICENSE-DATA-DOCS.md). The external graph catalogues retain the source attribution described in [THIRD_PARTY.md](THIRD_PARTY.md) and are excluded from that licence grant.

[SHA256SUMS.txt](SHA256SUMS.txt) records the checksum of every distributed file. The reproduction command checks these sums before beginning the mathematical calculations.
