import importlib.metadata

__all__ = [
    "bibliography",
]

url_optika = "https://optika.readthedocs.io"
"""The documentation of the raytracing package, which the prose links to."""


def bibliography() -> str:
    """
    The BibTeX entries the section cites, for the manuscript's bibliography.

    The version of the raytracing package is read from the installed
    package, so the entry names the version that produced the figures.
    """
    version_optika = importlib.metadata.version("optika")

    return f"""@SOFTWARE{{optika,
    author = {{{{Smart}}, Roy T. and {{Kankelborg}}, Charles C.}},
    title = {{Optika}},
    url = {{{url_optika}}},
    version = {{{version_optika}}},
    year = {{2026}},
}}
"""
