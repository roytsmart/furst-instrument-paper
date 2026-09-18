import pathlib
import shutil
import subprocess
import pytest
import matplotlib

matplotlib.use("agg")

import furst_instrument_paper
from furst_instrument_paper import _export

_document = r"""
\documentclass[twocolumn]{emulateapj}
\usepackage{graphicx}
\usepackage{hyperref}
\begin{document}
\title{Test}
\author{Test}
\begin{abstract}
Test.
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
the exported section and bibliography the way the collaborator will.
"""


def test_export(tmp_path: pathlib.Path):
    result = furst_instrument_paper.export(tmp_path)

    assert all(path.exists() for path in result)
    assert (tmp_path / _export.filename_section).exists()
    assert (tmp_path / _export.filename_bibliography).exists()
    assert (tmp_path / "figures" / "layout.pdf").exists()
    assert (tmp_path / "figures" / "lsf.pdf").exists()
    assert (tmp_path / "figures" / "resolvingPower.pdf").exists()

    latex = (tmp_path / _export.filename_section).read_text(encoding="utf-8")
    assert r"\subsection{Optical Performance}" in latex
    assert r"\newcommand{\ResolvingPowerMin}" in latex
    assert "figures/layout.pdf" in latex
    assert r"\label{tab:designParameters}" in latex
    assert r"\label{fig:layout}" in latex
    assert r"\label{fig:lsf}" in latex
    assert r"\label{fig:resolvingPower}" in latex
    assert r"\citep{optika}" in latex

    # every package the prose cites has an entry, and every entry is cited
    bib = (tmp_path / _export.filename_bibliography).read_text(encoding="utf-8")
    for item in furst_instrument_paper.software():
        assert f"@SOFTWARE{{{item.key}," in bib
        assert item.key in latex
        assert item.url in latex

    # a citation without a year is typeset as "????"
    assert bib.count("year = {") == len(furst_instrument_paper.software())


def _has_latex() -> bool:
    """Whether the section can be compiled on this machine."""
    for program in ("pdflatex", "bibtex", "kpsewhich"):
        if shutil.which(program) is None:
            return False
    for file in ("emulateapj.cls", "aasjournalv7.bst"):
        result = subprocess.run(
            ["kpsewhich", file],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False
    return True


def _run(command: list[str], cwd: pathlib.Path) -> None:
    """Run a step of the LaTeX build, failing with its output if it fails."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout[-3000:]


@pytest.mark.skipif(not _has_latex(), reason="needs pdflatex, bibtex, and emulateapj")
def test_compile(tmp_path: pathlib.Path):
    """The exported section compiles, with its references, in a manuscript."""
    furst_instrument_paper.export(tmp_path)
    (tmp_path / "test.tex").write_text(_document, encoding="utf-8")

    pdflatex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "test.tex"]
    _run(pdflatex, tmp_path)
    _run(["bibtex", "test"], tmp_path)
    _run(pdflatex, tmp_path)
    _run(pdflatex, tmp_path)

    assert (tmp_path / "test.pdf").exists()
    log = (tmp_path / "test.log").read_text(encoding="utf-8", errors="replace")
    assert "Undefined control sequence" not in log
    assert "undefined references" not in log
    assert "undefined citations" not in log
