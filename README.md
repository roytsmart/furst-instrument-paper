# furst-instrument-paper

Figures and numbers for the FURST instrument paper, generated from the
[`furst-optics`](https://github.com/Kankelborg-Group/furst-optics) model of
the instrument.

The manuscript itself lives in Overleaf. This package produces the pieces of
it that come from the optical model, so that they stay in sync with the model
instead of being drawn or typed by hand:

- `figures/<name>.pdf`, one PDF per figure, sized for the journal's column or
  text width, and
- `figures/<name>.tex`, the matching `figure` environment with the caption, and
- `variables.tex`, a `\newcommand` for every number the prose cites.

## Usage

Install the package, then export everything into a clone of the Overleaf
project:

```bash
pip install -e .[test]
python -c "import furst_instrument_paper; furst_instrument_paper.export('path/to/overleaf')"
```

In the manuscript, load the numbers in the preamble and place each figure where
it belongs:

```latex
\input{variables.tex}
...
\input{figures/layout.tex}
```

The figure files reference their images as `figures/<name>.pdf`, relative to
the main `.tex` file.

Every Overleaf project has a git remote at `https://git.overleaf.com/<project id>`,
so the exported files can be committed and pushed there like any other change.

## Tests

```bash
pytest
```

The tests build every figure, check every variable, and run the export into a
temporary directory.
