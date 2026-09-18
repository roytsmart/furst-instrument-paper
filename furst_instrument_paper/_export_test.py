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
\end{document}
"""
"""
A stand-in for the manuscript, in the class the draft uses, which includes
the exported section the way the collaborator will.
"""


def test_export(tmp_path: pathlib.Path):
    result = furst_instrument_paper.export(tmp_path)

    assert all(path.exists() for path in result)
    assert (tmp_path / _export.filename_section).exists()
    assert (tmp_path / "figures" / "layout.pdf").exists()
    assert (tmp_path / "figures" / "resolvingPower.pdf").exists()

    latex = (tmp_path / _export.filename_section).read_text(encoding="utf-8")
    assert r"\subsection{Optical Performance}" in latex
    assert r"\newcommand{\ResolvingPowerMin}" in latex
    assert "figures/layout.pdf" in latex
    assert r"\label{fig:layout}" in latex
    assert r"\label{fig:resolvingPower}" in latex


def _has_latex() -> bool:
    """Whether the section can be compiled on this machine."""
    if shutil.which("pdflatex") is None or shutil.which("kpsewhich") is None:
        return False
    result = subprocess.run(
        ["kpsewhich", "emulateapj.cls"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() != ""


@pytest.mark.skipif(not _has_latex(), reason="needs pdflatex and emulateapj")
def test_compile(tmp_path: pathlib.Path):
    """The exported section compiles when included in a manuscript."""
    furst_instrument_paper.export(tmp_path)
    (tmp_path / "test.tex").write_text(_document, encoding="utf-8")

    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "test.tex"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout[-3000:]

    assert (tmp_path / "test.pdf").exists()
    log = (tmp_path / "test.log").read_text(encoding="utf-8", errors="replace")
    assert "Undefined control sequence" not in log
    assert "undefined references" not in log
