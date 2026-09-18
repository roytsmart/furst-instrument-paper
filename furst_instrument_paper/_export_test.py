import pathlib
import matplotlib

matplotlib.use("agg")

import furst_instrument_paper


def test_export(tmp_path: pathlib.Path):
    result = furst_instrument_paper.export(tmp_path)

    assert all(path.exists() for path in result)
    assert (tmp_path / "variables.tex").exists()
    assert (tmp_path / "figures" / "layout.pdf").exists()
    assert (tmp_path / "figures" / "layout.tex").exists()

    latex = (tmp_path / "figures" / "layout.tex").read_text(encoding="utf-8")
    assert "figures/layout.pdf" in latex
    assert r"\label{fig:layout}" in latex
