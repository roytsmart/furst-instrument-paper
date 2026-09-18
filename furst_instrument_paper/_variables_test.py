import aastex
import furst_instrument_paper


def test_variables():
    result = furst_instrument_paper.variables()
    assert len(result) > 0
    for variable in result:
        assert isinstance(variable, aastex.Variable)
        assert variable.dumps().startswith(r"\newcommand")


def test_variables_unique():
    """Two variables with one name would silently overwrite each other."""
    result = furst_instrument_paper.variables()
    names = [variable.name for variable in result]
    assert len(names) == len(set(names))
