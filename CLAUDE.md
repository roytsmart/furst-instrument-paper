# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`furst-instrument-paper` supplies the model-derived parts of the FURST
instrument paper. Unlike the group's other paper repositories, it does **not**
generate the whole article: the manuscript is written by a collaborator in
Overleaf, and this package produces the figures and numbers that come from the
[`furst-optics`](https://github.com/Kankelborg-Group/furst-optics) model so
that they stay in sync with it.

`furst_instrument_paper.export(directory)` writes, into a clone of the Overleaf
project,

- `033_instrument_performance.tex`, subsection 3.3 *Optical Performance* as one
  file: a `\newcommand` for every number it cites, the prose, and the `figure`
  environments, so the manuscript includes it with a single `\input`, and
- `figures/<name>.pdf`, the image of each figure.

This is one package within the larger Kankelborg-Group workspace (see the
parent `../CLAUDE.md`). Use `named_arrays` (`import named_arrays as na`) rather
than `numpy` for array work.

## Commands

```bash
pip install -e .[test]
pytest                    # builds every figure and runs the export into a temp dir
black furst_instrument_paper
ruff check .
python -c "import furst_instrument_paper; furst_instrument_paper.export('path/to/overleaf')"
```

## Architecture

- `_instrument.py`: the final design from `furst.instruments.design()`, with
  seeded stratified random field and pupil samples drawn separately for each
  channel. Every performance figure traces this one instrument.
- `_performance.py`: the disk-integrated line spread function, its width
  (including the width of a pixel in quadrature), the dispersion, and the
  resolving power, following the original design study.
- `figures/`: one module per figure, each a function returning an
  `aastex.Figure` whose caption is written here. Figures are sized with
  `aastex.column_width_inches` or `aastex.text_width_inches` and styled with
  `_style.rc`.
- `_variables.py`: the `aastex.Variable` list. Add a variable rather than
  typing a number into the prose.
- `_bibliography.py`: the software the section cites, whose versions are read
  from the installed distributions.
- `_tables.py`: the comparison of the draft's design parameters with the
  model's, whose disagreements are flagged by hand on each row.
- `_section.py`: the prose of the section, citing only those variables, and
  the assembly of the exported file.
- `_export_figures.py` and `_export.py`: write the files above.

Publishing a release runs `.github/workflows/overleaf.yml`, which exports the
section, attaches it to the release, and pushes it to the Overleaf project
using the `OVERLEAF_TOKEN` and `OVERLEAF_PROJECT_ID` secrets.

Each figure and variable has a test, `_section_test.py` checks that the prose
cites no undefined macro, `_export_test.py` compiles the section in a stand-in
emulateapj manuscript when LaTeX is available, and `_performance_test.py`
asserts the resolving power requirement is met everywhere, so a model change
that breaks the paper's claims fails CI.
