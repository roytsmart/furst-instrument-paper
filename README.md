# furst-instrument-paper

[![tests](https://github.com/roytsmart/furst-instrument-paper/actions/workflows/tests.yml/badge.svg)](https://github.com/roytsmart/furst-instrument-paper/actions/workflows/tests.yml)
[![pdf](https://github.com/roytsmart/furst-instrument-paper/actions/workflows/pdf.yml/badge.svg)](https://github.com/roytsmart/furst-instrument-paper/actions/workflows/pdf.yml)

Figures and numbers for the FURST instrument paper, generated from the
[`furst-optics`](https://github.com/Kankelborg-Group/furst-optics) model of
the instrument.

**[Read the current section](https://roytsmart.github.io/furst-instrument-paper/optical-performance.pdf)**,
rebuilt from the model on every push to `main`. It is the exported section
inside the smallest manuscript that can hold it, so it shows exactly what the
corresponding author will get.

The manuscript itself lives in Overleaf. This package produces the part of it
that comes from the optical model, subsection 3.3, *Optical Performance*, so
that it stays in sync with the model instead of being drawn or typed by hand:

- `033_instrument_performance.tex`, one file holding a `\newcommand` for
  every number the section cites, the text of the section, and its figures,
- `033_instrument_performance.bib`, the references the section cites, and
- `figures/<name>.pdf`, the image of each figure, sized for the journal's
  column or text width.

## Usage

Install the package, then export into a clone of the Overleaf project:

```bash
pip install -e .[test]
python -c "import furst_instrument_paper; furst_instrument_paper.export('path/to/overleaf')"
```

In the manuscript, include the section where subsection 3.3 belongs:

```latex
\input{033_instrument_performance.tex}
```

The figures are referenced as `figures/<name>.pdf`, relative to the main
`.tex` file, and the section's macros are available to the rest of the
manuscript after the `\input`. The section links to the documentation of the
raytracing package with `\href`, so the manuscript needs `hyperref`, and it
cites the package with `\citep`, so `033_instrument_performance` should be
added to the manuscript's `\bibliography`.

Every Overleaf project has a git remote at `https://git.overleaf.com/<project id>`,
so the exported files can be committed and pushed there like any other change.

## Delivery

Publishing a release runs the `overleaf` workflow, which exports the section,
attaches it to the release, and pushes it to the Overleaf project as a single
commit. The same workflow can be run by hand from the Actions tab to deliver
without cutting a version.

It needs two repository secrets, and warns and skips the push without them:

| Secret | Value |
|---|---|
| `OVERLEAF_TOKEN` | A git authentication token from Overleaf's account settings |
| `OVERLEAF_PROJECT_ID` | The part of the project's git URL after `git.overleaf.com/` |

The workflow only ever writes the files this package owns, and clones the
project fresh each time, since Overleaf refuses a push that is not a
fast-forward.

## Tests

```bash
pytest
```

The tests build every figure, check every variable, run the export into a
temporary directory, and, where `pdflatex` and the `emulateapj` class are
available, compile the exported section inside a stand-in manuscript. That
last test is skipped by the `tests` workflow, which has no LaTeX, and runs in
the `pdf` workflow, which does.

To build the preview locally:

```bash
python -c "import furst_instrument_paper; furst_instrument_paper.preview('preview')"
```
