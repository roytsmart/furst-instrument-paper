import pathlib
import furst_instrument_paper
from ._export_figures import save_figures

__all__ = [
    "filename_section",
    "filename_section_response",
    "export",
]

filename_section = "033_instrument_performance.tex"
"""
The file, inside the manuscript, that the section is written to.

Named for its place in the manuscript, subsection 3.3, so that it sorts
beside the collaborator's own section files.
"""

filename_section_response = "034_response.tex"
"""
The file, inside the manuscript, that the response section is written to.

Numbered to follow the optical performance section, as subsection 3.4.
"""

filename_bibliography = "033_instrument_performance.bib"
"""The file, inside the manuscript, that the sections' references are written to."""


def export(directory: str | pathlib.Path) -> list[pathlib.Path]:
    """
    Write the optical performance and response sections and their figures
    into a copy of the manuscript.

    Each section is one ``.tex`` file which defines its macros, gives its
    text, and places its figures, so the manuscript includes it with a single
    ``\\input``. The images of the figures are written beside them, in the
    figures directory, and are referenced relative to the main file of the
    manuscript. The references the sections cite are written to one ``.bib``
    file for the manuscript to add to its bibliography.

    Parameters
    ----------
    directory
        The root of the manuscript, where its main ``.tex`` file lives.

    Returns
    -------
    The files that were written.
    """
    directory = pathlib.Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    written = save_figures(directory)

    path = directory / filename_section
    path.write_text(furst_instrument_paper.section(), encoding="utf-8")
    written.append(path)

    path = directory / filename_section_response
    path.write_text(furst_instrument_paper.section_response(), encoding="utf-8")
    written.append(path)

    path = directory / filename_bibliography
    path.write_text(furst_instrument_paper.bibliography(), encoding="utf-8")
    written.append(path)

    return written
