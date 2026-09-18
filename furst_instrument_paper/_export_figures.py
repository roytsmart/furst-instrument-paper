import pathlib
import aastex
import furst_instrument_paper

__all__ = [
    "directory_figures",
    "figures",
    "figures_latex",
    "save_figures",
]

directory_figures = "figures"
"""The directory, inside the manuscript, that the figure images are written to."""


def figures() -> list[aastex.Figure]:
    """Every figure of the section, built from the model."""
    return [
        furst_instrument_paper.figures.layout(),
        furst_instrument_paper.figures.lsf(),
        furst_instrument_paper.figures.lsf_width(),
        furst_instrument_paper.figures.resolving_power(),
    ]


def _latex(figure: aastex.Figure) -> str:
    """
    The ``figure`` environment of a figure, referencing its image inside the
    figures directory, relative to the main file of the manuscript.
    """
    latex = figure.dumps()
    for image in figure.images:
        latex = latex.replace(
            f"{{{image.name}}}",
            f"{{{directory_figures}/{image.name}}}",
        )
    return latex


def figures_latex() -> str:
    """The ``figure`` environments of every figure, one after another."""
    return "\n\n".join(_latex(figure) for figure in figures())


def save_figures(directory: str | pathlib.Path) -> list[pathlib.Path]:
    """
    Write the image of every figure into the figures directory of the
    manuscript.

    Parameters
    ----------
    directory
        The root of the manuscript.
    """
    directory = pathlib.Path(directory) / directory_figures
    directory.mkdir(parents=True, exist_ok=True)

    written = []
    for figure in figures():
        for image in figure.images:
            path = directory / image.name
            image.figure.savefig(path, *image.args, **image.kwargs)
            written.append(path)
    return written
