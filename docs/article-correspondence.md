# Agreement with the article

The finite inputs are linked to a specific manuscript, rather than to a mutable filename. [ARTICLE.md](../ARTICLE.md) gives its bibliographic context and the relationship to the public article locator. [The correspondence record](../data/article_correspondence.json) identifies the 23-page scientific text by its PDF SHA-256 and records the source of each table and figure.

The authors copied the three seed tables and all figure sources byte for byte and recorded the comparison in the preparation records. This source-to-source comparison is an attestation by the authors, not an operation performed by the public script. The seven small graphs, their reductions, the extension counts and the four octahedral reductions are verbatim `tabular` environments extracted from the article. The sixteen-vertex seed and its profiles are verbatim equation environments. Each extract records the whole source file's hash, its LaTeX label and its own hash. The complete article source is not needed to run the calculations.

```text
python reproduce.py --only correspondence
```

This checks the extract bytes against their recorded identities and compares the extracted values with the inputs used by the calculations. The other groups check the reductions, incidences, clique counts and classifications themselves. A checksum identifies a document; it does not prove its mathematics. The reproduction program does not parse the layout of a PDF.

If you have a copy of the identified manuscript, you may also run:

```text
python reproduce.py --only correspondence --article-pdf /path/to/manuscript.pdf
```

The record accepts the identified scientific manuscript and its citation-only derivative. A PDF rebuilt by another service, including arXiv, generally has a different hash even when its mathematical text agrees. An unrecognised PDF produces a failed identity check after the selected mathematical checks; their separate results remain in the report. The ordinary reproduction route needs only this repository and Python's standard library.
