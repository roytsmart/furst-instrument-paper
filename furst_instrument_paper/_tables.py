import dataclasses
import furst_instrument_paper

__all__ = [
    "design_parameters",
]

label = "tab:designParameters"
"""The label of the table, for the prose to refer to."""

date_draft = "September 18, 2026"
"""The date of the draft whose Table 3 is transcribed here."""


@dataclasses.dataclass(frozen=True)
class _Row:
    """One parameter of the design, as the draft and the model give it."""

    parameter: str
    """The name of the parameter."""

    draft: str
    """The value in Table 3 of the draft, transcribed as written."""

    model: str
    """The value from the model, written with the macros of the section."""

    differs: bool = False
    """
    Whether the two values disagree and need to be reconciled.

    Judged by hand rather than compared as numbers, since the two columns
    round differently and some entries are not numbers at all.
    """


def _rows() -> list[_Row]:
    """
    The rows of the table.

    The draft column is Table 3 of the draft of :data:`date_draft`, copied
    as written. The model column cites the macros defined at the top of the
    exported section, so it follows the model.
    """
    instrument = furst_instrument_paper.instrument()
    detector = instrument.camera.sensor.family

    return [
        _Row(
            parameter="Wavelength range",
            draft=r"116 to 185\,nm",
            model=r"\WavelengthMin\ to \WavelengthMax",
        ),
        _Row(
            parameter=r"Resolving power",
            draft=r"$> 20{,}000$",
            model=r"\ResolvingPowerMin\ to \ResolvingPowerMax",
        ),
        _Row(
            parameter="Number of feed optics",
            draft="7",
            model=r"\NumChannels",
        ),
        _Row(
            parameter="Radius of feed optic",
            draft=r"3\,mm",
            model=r"\FeedOpticRadius",
        ),
        _Row(
            parameter="Height of feed optic",
            draft=r"38\,mm",
            model=r"\FeedOpticHeight\ (clear aperture)",
            differs=True,
        ),
        _Row(
            parameter="Feed optic positions (from grating normal)",
            draft=r"10.5\arcdeg\ to 17.9\arcdeg",
            model=r"\AngleIncidenceMin\ to \AngleIncidenceMax",
        ),
        _Row(
            parameter="Radius of grating",
            draft=r"1359\,mm",
            model=r"\GratingRadius",
            differs=True,
        ),
        _Row(
            parameter="UV section of grating",
            draft=r"200\,mm $\times$ 30\,mm",
            model=r"\GratingWidthClear\ $\times$ \GratingHeightClear\ (clear aperture)",
            differs=True,
        ),
        _Row(
            parameter="Groove density",
            draft=r"1.97\,gr/\micron",
            model=r"\GratingRulingDensity",
            differs=True,
        ),
        _Row(
            parameter="Detector type",
            draft="CCD230-42",
            model=detector,
        ),
        _Row(
            parameter="Detector format",
            draft=r"2048 $\times$ 1024",
            model=r"\NumPixelX\ $\times$ \NumPixelY",
            differs=True,
        ),
        _Row(
            parameter="Pixel size",
            draft=r"15\,\micron",
            model=r"\PixelWidth",
        ),
        _Row(
            parameter="CCD position (from grating normal)",
            draft=r"4.98\arcdeg",
            model=r"\AngleDiffraction",
        ),
    ]


def _cell(text: str, bold: bool) -> str:
    """A cell of the table, set in bold if it is one of the disagreements."""
    return rf"\textbf{{{text}}}" if bold else text


def design_parameters() -> str:
    """
    The LaTeX of a table comparing the design parameters of the draft with
    those of the model.

    Meant for the coauthors while the two are reconciled: the entries which
    disagree are set in bold, and the caption says so.
    """
    lines = [
        r"\begin{table*}[!ht]",
        r"\centering",
        r"\caption{",
        r"Optical design parameters of the instrument model used in this section,",
        rf"beside the values in Table~3 of the draft of {date_draft}.",
        r"Entries in bold differ between the two and need to be reconciled",
        r"before submission.",
        r"}",
        rf"\label{{{label}}}",
        r"\begin{tabular}{lll}",
        r"\hline",
        r"Parameter & Draft & Model \\",
        r"\hline",
    ]
    for row in _rows():
        lines.append(
            " & ".join(
                [
                    row.parameter,
                    _cell(row.draft, row.differs),
                    _cell(row.model, row.differs),
                ]
            )
            + r" \\"
        )
    lines += [
        r"\hline",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines)
