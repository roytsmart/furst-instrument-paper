"""
Figures and numbers for the FURST instrument paper, generated from the
:mod:`furst` model of the instrument.
"""

from . import figures
from ._instrument import instrument
from ._performance import performance
from ._variables import variables
from ._export import export

__all__ = [
    "figures",
    "instrument",
    "performance",
    "variables",
    "export",
]
