# furst-instrument-paper

Figures and numbers for the FURST instrument paper, generated from the
[`furst-optics`](https://github.com/Kankelborg-Group/furst-optics) model of
the instrument.

The manuscript itself lives in Overleaf. This package produces the part of it
that comes from the optical model, subsection 3.3, *Optical Performance*, so
that it stays in sync with the model instead of being drawn or typed by hand:

- `033_instrument_performance.tex`, one file holding a `\newcommand` for
  every number the section cites, the text of the section, and its figures, and
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
manuscript after the `\input`.

Every Overleaf project has a git remote at `https://git.overleaf.com/<project id>`,
so the exported files can be committed and pushed there like any other change.

## Tests

```bash
pytest
```

The tests build every figure, check every variable, run the export into a
temporary directory, and, where `pdflatex` and the `emulateapj` class are
available, compile the exported section inside a stand-in manuscript.
