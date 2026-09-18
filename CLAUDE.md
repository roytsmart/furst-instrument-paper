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

- `figures/<name>.pdf` and `figures/<name>.tex` for every figure, the latter a
  complete `figure` environment with caption and label, and
- `variables.tex`, one `\newcommand` per number the prose cites.

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
  typing a number into the manuscript.
- `_export.py`: writes the files above.

Each figure and variable has a test, and `_performance_test.py` asserts the
resolving power requirement is met everywhere, so a model change that breaks
the paper's claims fails CI.
