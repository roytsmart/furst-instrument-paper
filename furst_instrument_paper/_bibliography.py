import datetime
import dataclasses
import importlib.metadata

__all__ = [
    "software",
    "bibliography",
]


@dataclasses.dataclass(frozen=True)
class _Software:
    """A software package the section cites."""

    key: str
    """The BibTeX key the prose cites it by."""

    package: str
    """The name of the installed distribution, which gives the version."""

    title: str
    """The title of the entry."""

    authors: tuple[str, ...]
    """The authors, each written as ``{Family}, Given``."""

    url: str
    """
    Where a reader is sent to find it.

    The documentation where the package has some, and its repository
    otherwise. The prose links to this same address.
    """


optika = _Software(
    key="optika",
    package="optika",
    title="Optika",
    authors=("{Smart}, Roy T.", "{Kankelborg}, Charles C."),
    url="https://optika.readthedocs.io",
)
"""The raytracing package the instrument model is built with."""

furst_optics = _Software(
    key="furstOptics",
    package="furst-optics",
    title="furst-optics",
    authors=("{Smart}, Roy T.",),
    url="https://furst-optics.readthedocs.io",
)
"""The model of the FURST optical system."""

furst_instrument_paper = _Software(
    key="furstInstrumentPaper",
    package="furst-instrument-paper",
    title="furst-instrument-paper",
    authors=("{Smart}, Roy T.",),
    url="https://github.com/roytsmart/furst-instrument-paper",
)
"""The package which generates this section."""


def software() -> list[_Software]:
    """Every software package the section cites."""
    return [optika, furst_optics, furst_instrument_paper]


references = (
    r"""@techreport{Stock2023,
    author = {{Stock}, Carsten},
    title = {{FURST FUV Grating: Final Report}},
    institution = {Carl Zeiss Jena GmbH},
    year = {2023},
    month = jul,
}""",
    r"""@article{Heymes2020,
    author = {{Heymes}, Julian and {Soman}, Matthew and {Randall}, George and {Gottwald}, Alexander and {Harris}, Andrew and {Kelt}, Andrew and {Moody}, Ian and {Meng}, Xiao and {Holland}, Andrew D.},
    title = {{Comparison of Back-Thinned Detector Ultraviolet Quantum Efficiency for Two Commercially Available Passivation Treatments}},
    journal = {IEEE Transactions on Nuclear Science},
    year = {2020},
    volume = {67},
    number = {8},
    pages = {1962--1967},
    doi = {10.1109/TNS.2020.3001622},
}""",
    r"""@article{Ramanathan2020,
    author = {{Ramanathan}, K. and {Kurinsky}, N.},
    title = {{Ionization yield in silicon for eV-scale electron-recoil processes}},
    journal = {Phys. Rev. D},
    year = {2020},
    volume = {102},
    number = {6},
    pages = {063026},
    doi = {10.1103/PhysRevD.102.063026},
}""",
)
"""
The literature the section cites, besides software: the final report on the
flight grating, and the sources of the models of the detector.
"""


def _entry(item: _Software) -> str:
    """
    One BibTeX entry, naming the installed version of the package.

    The version is read from the installed distribution rather than written
    down, so each entry names the version which produced the figures, and
    the year is the year that version was used, which is the convention for
    citing software.
    """
    authors = " and ".join(item.authors)
    version = importlib.metadata.version(item.package)
    year = datetime.date.today().year
    return "\n".join(
        [
            f"@SOFTWARE{{{item.key},",
            f"    author = {{{authors}}},",
            f"    title = {{{item.title}}},",
            f"    url = {{{item.url}}},",
            f"    version = {{{version}}},",
            f"    year = {{{year}}},",
            "}",
        ]
    )


def bibliography() -> str:
    """
    The BibTeX entries the section cites, for the manuscript's bibliography.
    """
    entries = [_entry(item) for item in software()] + list(references)
    return "\n".join(entries) + "\n"
