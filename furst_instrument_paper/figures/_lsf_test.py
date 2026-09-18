import pytest
import matplotlib

matplotlib.use("agg")

import matplotlib.pyplot as plt
import aastex
import furst_instrument_paper


def test_lsf():
    result = furst_instrument_paper.figures.lsf()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:lsf}" in result.dumps()
    assert len(result.images) == 1


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")
