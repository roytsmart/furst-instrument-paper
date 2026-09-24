"""
Figures and numbers for the FURST instrument paper, generated from the
:mod:`furst` model of the instrument.
"""

from . import figures
from ._instrument import instrument
from ._performance import Performance, performance
from ._radiometry import Radiometry, radiometry
from ._variables import variables
from ._section import section
from ._bibliography import software, bibliography
from ._export import export
from ._preview import preview

__all__ = [
    "figures",
    "instrument",
    "Performance",
    "performance",
    "Radiometry",
    "radiometry",
    "variables",
    "section",
    "software",
    "bibliography",
    "export",
    "preview",
]
