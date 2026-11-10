# Reproducing the finite calculations

The calculations answer concrete mathematical questions: does each displayed fold satisfy the required neighbourhood inclusion, does each certificate prove the stated membership or non-membership, and do the listed clique counts and homology groups follow from the given graphs? The scripts read the distributed graphs and witnesses, carry out these checks, and collect the answers by result.

## Obtain the material

Download [strictly-k-dismantlable-graphs-v1.0.0.zip](https://github.com/Geometric-and-Combinatorial-Structures/strictly-k-dismantlable-graphs/releases/download/v1.0.0/strictly-k-dismantlable-graphs-v1.0.0.zip) from release `v1.0.0` and extract it. This is the same archive used by the notebook. The extracted directory contains `reproduce.py`, `generate.py` and the mathematical supplement. Open a terminal in that directory.

The calculations require **Python 3.11 or later**, with no additional mathematical packages. Check your installation with `python --version`. On systems where Python is called `python3`, use `python3` in the commands below. On Windows, `py -3` is another usual way to invoke the installed Python interpreter.

For a browser-based calculation, [open the notebook in Google Colab](https://colab.research.google.com/github/Geometric-and-Combinatorial-Structures/strictly-k-dismantlable-graphs/blob/v1.0.0/notebooks/reproduce.ipynb). Choose **Runtime → Run all**. The notebook obtains release `v1.0.0`, explains the mathematical purpose of each calculation and uses the same scripts as the local route. A Google account is needed to execute cells in Colab.

## Run the required checks

```text
python reproduce.py
```

The first check compares the files with their distributed SHA-256 sums. The remaining checks follow the constructions and the supplement:

1. **The article's $3k+8$ family.** Verify the eleven-vertex seed, its level-one reduction and exclusion from level zero, the fold reduction after deleting the first centre, all thirteen clique rows, and the exact incidences drawn in the three figures.
2. **The $4k+4$ family.** Verify the seven roots asserting the levels of the two prefixes, the sixteen-vertex seed and its remainder, together with all nineteen neighbourhood clique rows.
3. **The $6k+6$ family.** Verify both positive reductions, all fourteen inner folds, every displayed neighbourhood inclusion, the twelve first-fold obstructions and all seventeen clique rows.
4. **Kernel completion and homology.** Recover the eleven-vertex kernel, compute its reduced homology and that of its neighbourhoods, and check the degree shifts and boundary conventions over $\mathbb F_2$.
5. **Further controls.** Compare two independent implementations of the six adjacency rules for the layered graphs at levels $1,\ldots,6$, and compare the two smaller prefixes of $H_k$ with their separate graph encodings. Check single-vertex deletions from $F_k$ for $k=2,3,4$, reject altered certificates, and test all ten templates with a one-vertex seed and one or two auxiliary types, at zero to three layers.

A successful run ends with `PASS` and the location of its output directory. The directory contains:

| File | Contents |
| --- | --- |
| `report.txt` | A readable list of the mathematical checks and their outcomes. |
| `report.json` | Computed values, finite ranges, elapsed times, source checksums and any failure or interruption. |

Each run creates a different directory beneath `results/`. To choose another location, append `--output` followed by a **new** directory name. An existing output directory is refused, preserving earlier results. Inputs are checked again at the end to ensure that they have not changed during the calculation.

`FAIL` means that a required comparison or proof check did not succeed; the report names the failing check. `INCONCLUSIVE` means that the calculation was interrupted before completion. Later checks that did not run are listed separately. If the process is terminated forcibly before it can save a report, the absence of a completed report is likewise not evidence of success.

## Inspect one result

The [correspondence table](results.md) gives a command for each group. For example:

```text
python reproduce.py --only 4k4
```

This verifies the seven roots and nineteen clique rows for $H_k$, and the direct proof for its eight-vertex prefix. A positive root supplies an admissible first deletion and certificates for its neighbourhood and remainder. A negative root supplies, for every possible first vertex, a certificate that at least one of those required conditions fails. The [certificate description](certificates.md) gives the exact rules and explains why the resulting finite proof is valid.

## Check the additional finite ranges

A **layer template** consists of a seed, a number of auxiliary types, their profiles, and the type graph. These finite data determine every layer.

```text
python reproduce.py --extended
```

In addition to the main checks, this enumerates **every labelled seed on one, two or three vertices**, every choice of profiles for one or two auxiliary types, and every type graph. It checks the construction, centre neighbourhoods, folds and Euler identities at zero, one, two and three layers. It computes the homological shifts for all templates whose seed has at most two vertices. It also checks the kernel identities for every graph on at most three vertices and every ordered pair of profiles covering that graph.

The report states these ranges and the number of identities checked. The first layer supplies the base case of each shift identity; the later layers test its propagation. These are finite tests of the formulas, not an inference from a sample to all graphs or all levels. The corresponding universal statements are proved in the supplement. Runtime depends on the machine; there is no search deadline whose expiry is interpreted as non-membership.

## Read or compile the supplement

The [PDF](../supplement/supplement.pdf) is included, so LaTeX is optional. To compile the sources with a TeX installation containing the usual AMS, Palatino, Euler and TikZ packages, run the following from the `supplement` directory:

```text
latexmk -pdf -outdir=../results/latex main.tex
```

This places the generated document and auxiliary files under `results/latex`, leaving the distributed PDF and sources unchanged. The PDF contains linked section and result numbers, numerical citations, and blue italic text when a new concept is defined.
