import pytest
import aastex
import furst_instrument_paper


@pytest.mark.parametrize(
    argnames="func",
    argvalues=[
        furst_instrument_paper.variables,
        furst_instrument_paper.variables_response,
    ],
)
def test_variables(func):
    result = func()
    assert len(result) > 0
    for variable in result:
        assert isinstance(variable, aastex.Variable)
        assert variable.dumps().startswith(r"\newcommand")


def test_variables_unique():
    """
    Two variables with one name would silently overwrite each other, and
    since both exported files go into one manuscript, the names must be
    unique across both.
    """
    result = furst_instrument_paper.variables()
    result = result + furst_instrument_paper.variables_response()
    names = [variable.name for variable in result]
    assert len(names) == len(set(names))
