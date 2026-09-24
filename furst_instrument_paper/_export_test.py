import re
import pathlib
import pytest
import matplotlib

matplotlib.use("agg")

import furst_instrument_paper
from furst_instrument_paper import _bibliography, _export, _preview


def test_export(tmp_path: pathlib.Path):
    result = furst_instrument_paper.export(tmp_path)

    assert all(path.exists() for path in result)
    assert (tmp_path / _export.filename_section).exists()
    assert (tmp_path / _export.filename_bibliography).exists()
    assert (tmp_path / "figures" / "layout.pdf").exists()
    assert (tmp_path / "figures" / "lsf.pdf").exists()
    assert (tmp_path / "figures" / "resolvingPower.pdf").exists()
    assert (tmp_path / "figures" / "effectiveArea.pdf").exists()

    latex = (tmp_path / _export.filename_section).read_text(encoding="utf-8")
    assert r"\subsection{Optical Performance}" in latex
    assert r"\newcommand{\ResolvingPowerMin}" in latex
    assert "figures/layout.pdf" in latex
    assert r"\label{tab:designParameters}" in latex
    assert r"\label{fig:layout}" in latex
    assert r"\label{fig:lsf}" in latex
    assert r"\label{fig:resolvingPower}" in latex
    assert r"\label{fig:effectiveArea}" in latex
    assert r"\label{tab:throughput}" in latex
    assert r"\citep{optika}" in latex

    # every package the prose cites has an entry, and every entry is cited
    bib = (tmp_path / _export.filename_bibliography).read_text(encoding="utf-8")
    for item in furst_instrument_paper.software():
        assert f"@SOFTWARE{{{item.key}," in bib
        assert item.key in latex
        assert item.url in latex

    # and so has every other reference, each of which is cited
    for entry in _bibliography.references:
        key = re.match(r"@\w+\{(\w+),", entry).group(1)
        assert key in bib
        assert key in latex

    # a citation without a year is typeset as "????"
    num_entries = len(furst_instrument_paper.software()) + len(_bibliography.references)
    assert bib.count("year = {") == num_entries


@pytest.mark.skipif(
    not _preview.has_latex(),
    reason="needs pdflatex, bibtex, and the journal's class and style",
)
def test_preview(tmp_path: pathlib.Path):
    """The exported section compiles, with its references, in a manuscript."""
    result = furst_instrument_paper.preview(tmp_path)

    assert result.exists()

    log = (tmp_path / f"{_preview.name}.log").read_text(
        encoding="utf-8",
        errors="replace",
    )
    assert "Undefined control sequence" not in log
    assert "undefined references" not in log
    assert "undefined citations" not in log
