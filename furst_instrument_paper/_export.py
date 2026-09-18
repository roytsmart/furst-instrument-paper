import pathlib
import aastex
import furst_instrument_paper

__all__ = [
    "export",
]

directory_figures = "figures"
"""The directory, inside the manuscript, that the figures are written to."""

filename_variables = "variables.tex"
"""The file, inside the manuscript, that the variables are written to."""


def _figures() -> list[aastex.Figure]:
    """Every figure of the article, built from the model."""
    return [
        furst_instrument_paper.figures.layout(),
        furst_instrument_paper.figures.resolving_power(),
    ]


def _stem(figure: aastex.Figure) -> str:
    """The name a figure's files are saved under, taken from its label."""
    label = figure.label
    if isinstance(label, str):
        return label.split(":", 1)[-1]
    return label.marker.name


def export(directory: str | pathlib.Path) -> list[pathlib.Path]:
    """
    Write every figure and variable into a copy of the manuscript.

    Each figure becomes a PDF and a ``.tex`` file holding its ``figure``
    environment, both in the figures directory, and the variables become one
    file of ``\\newcommand`` definitions at the top level.
    The ``.tex`` files reference their images relative to the main file of
    the manuscript, so the manuscript can ``\\input`` them as they are.

    Parameters
    ----------
    directory
        The root of the manuscript, where its main ``.tex`` file lives.

    Returns
    -------
    The files that were written.
    """
    directory = pathlib.Path(directory)
    directory_figure = directory / directory_figures
    directory_figure.mkdir(parents=True, exist_ok=True)

    written = []

    for figure in _figures():
        latex = figure.dumps()
        for image in figure.images:
            path = directory_figure / image.name
            image.figure.savefig(path, *image.args, **image.kwargs)
            written.append(path)
            latex = latex.replace(
                f"{{{image.name}}}",
                f"{{{directory_figures}/{image.name}}}",
            )
        path = directory_figure / f"{_stem(figure)}.tex"
        path.write_text(latex + "\n", encoding="utf-8")
        written.append(path)

    path = directory / filename_variables
    lines = [variable.dumps() for variable in furst_instrument_paper.variables()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(path)

    return written
