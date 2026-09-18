import pathlib
import shutil
import subprocess
import furst_instrument_paper

__all__ = [
    "name",
    "document",
    "has_latex",
    "preview",
]

name = "optical-performance"
"""The name of the preview document, without an extension."""

document = r"""
\documentclass[twocolumn]{emulateapj}
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}

\title{The FURST Optical Performance Section}
\author{Roy T. Smart}

\begin{abstract}
This document is not the FURST instrument paper.
It is a preview of the one section of it which is generated from the
instrument model, built so that the section can be read and checked on its
own before it is delivered to the manuscript.
The numbered subsections above it are empty placeholders, standing in for
the sections of the manuscript which precede it.
\end{abstract}

\section{Instrument Overview}
\subsection{Design Rationale}
\subsection{Optical Layout}
\input{033_instrument_performance.tex}

\bibliographystyle{aasjournalv7}
\bibliography{033_instrument_performance}

\end{document}
"""
"""
A stand-in for the manuscript, in the class the draft uses, which includes
the exported section the way the corresponding author will.
"""

_programs = ("pdflatex", "bibtex", "kpsewhich")
"""The programs needed to compile the preview."""

_files = ("emulateapj.cls", "aasjournalv7.bst")
"""The LaTeX files needed to compile the preview."""


def has_latex() -> bool:
    """
    Whether this machine can compile the preview.

    The document is built with the class and bibliography style of the
    journal, which a plain LaTeX installation does not carry.
    """
    for program in _programs:
        if shutil.which(program) is None:
            return False
    for file in _files:
        result = subprocess.run(
            ["kpsewhich", file],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False
    return True


def _run(command: list[str], directory: pathlib.Path) -> None:
    """Run one step of the build, raising with its output if it fails."""
    result = subprocess.run(
        command,
        cwd=directory,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"{command[0]} failed in {directory}:\n{result.stdout[-3000:]}"
        )


def preview(directory: str | pathlib.Path) -> pathlib.Path:
    """
    Export the section and compile it inside a stand-in manuscript.

    The preview is how the section is read before it is delivered: it is
    the exported files, unmodified, inside the smallest document which can
    hold them.

    Parameters
    ----------
    directory
        Where to build the preview.

    Returns
    -------
    The compiled PDF.
    """
    directory = pathlib.Path(directory)
    furst_instrument_paper.export(directory)

    (directory / f"{name}.tex").write_text(document.lstrip("\n"), encoding="utf-8")

    pdflatex = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"{name}.tex",
    ]

    # twice after the bibliography, so that the citations and the references
    # to the figures and the table both settle
    _run(pdflatex, directory)
    _run(["bibtex", name], directory)
    _run(pdflatex, directory)
    _run(pdflatex, directory)

    return directory / f"{name}.pdf"
