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
  environments, so the manuscript includes it with a single `\input`,
- `034_response.tex`, subsection 3.4 *Response*, built the same way: the
  efficiency of each optic, the quantum efficiency of the detector in
  electrons per photon, and the response of the instrument,
- `033_instrument_performance.bib`, the references both files cite, and
- `figures/<name>.pdf`, the image of each figure.

Each `.tex` file defines only the macros it cites, and no macro is defined by
both, since the manuscript inputs both.

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

- `_instrument.py`: the instrument as it was built and flown, from
  `furst.instruments.as_built()`, with seeded stratified random field and
  pupil samples drawn separately for each channel. Every performance figure
  traces this one instrument.
- `_performance.py`: the disk-integrated line spread function, its width
  (including the width of a pixel in quadrature), the dispersion, and the
  resolving power, following the original design study.
- `_radiometry.py`: the effective area, the terms it is the product of
  (feed optic reflectance, grating efficiency, filter transmission, detector
  absorbance), the quantum efficiency of the detector in electrons per
  photon (absorbance times charge collection efficiency times quantum
  yield, not corrected for the yield), and the response per unit energy, in
  e- cm^2 erg^-1, following the design report of `furst-optics`.
- `figures/`: one module per figure, each a function returning an
  `aastex.Figure` whose caption is written here. Figures are sized with
  `aastex.column_width_inches` or `aastex.text_width_inches` and styled with
  `_style.rc`.
- `_variables.py`: the `aastex.Variable` lists, `variables()` for the optical
  performance section and `variables_response()` for the response section.
  Add a variable rather than typing a number into the prose.
- `_bibliography.py`: the software the sections cite, whose versions are read
  from the installed distributions, and the other references they cite.
- `_tables.py`: the comparison of the draft's design parameters (its Table 3)
  with the model's, whose disagreements are flagged by hand on each row, in
  the optical performance section, and of the terms of its effective area
  (its Table 4) with the model's, in the response section.
- `_section.py`: the prose of each section, citing only its own variables,
  and the assembly of each exported file.
- `_export_figures.py` and `_export.py`: write the files above.

- `_preview.py`: the stand-in manuscript and `preview()`, which exports both
  sections into it and compiles it. Both the compile test and CI use this.

`.github/workflows/pdf.yml` runs the tests with LaTeX installed, so the
compile test actually runs, then builds the preview and publishes it to the
`gh-pages` branch, served at
<https://roytsmart.github.io/furst-instrument-paper/optical-performance.pdf>.

Publishing a release runs `.github/workflows/overleaf.yml`, which exports the
sections, attaches them to the release, and pushes it to the Overleaf project
using the `OVERLEAF_TOKEN` and `OVERLEAF_PROJECT_ID` secrets.

Each figure and variable has a test, `_section_test.py` checks that the prose
of each section cites no macro its file does not define,
`_variables_test.py` that no macro is defined by both files,
`_export_test.py` compiles both sections in a stand-in
emulateapj manuscript when LaTeX is available, and `_performance_test.py`
asserts the resolving power requirement is met everywhere, so a model change
that breaks the paper's claims fails CI.
