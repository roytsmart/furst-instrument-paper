import dataclasses
import furst_instrument_paper

__all__ = [
    "design_parameters",
    "throughput",
]

label = "tab:designParameters"
"""The label of the table, for the prose to refer to."""

label_throughput = "tab:throughput"
"""The label of the table of the terms of the effective area."""

date_draft = "September 18, 2026"
"""The date of the draft whose Tables 3 and 4 are transcribed here."""


@dataclasses.dataclass(frozen=True)
class _Row:
    """One parameter of the design, as the draft and the model give it."""

    parameter: str
    """The name of the parameter."""

    draft: str
    """The value in the draft, transcribed as written."""

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
        ),
        _Row(
            parameter="UV section of grating",
            draft=r"200\,mm $\times$ 30\,mm",
            model=r"\GratingWidthClear\ $\times$ \GratingHeightClear\ (ruled area)",
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


def _rows_throughput() -> list[_Row]:
    """
    The rows of the table of the terms of the effective area.

    The draft column is Table 4 of the draft of :data:`date_draft`, copied
    as written, with its quantum yield from Table 5. The model column cites
    the macros defined at the top of the exported section.
    """
    return [
        _Row(
            parameter="Geometric area",
            draft=r"3.072\,mm$^2$",
            model=r"\AreaCollecting",
        ),
        _Row(
            parameter="Mirror reflectivity",
            draft=r"85\%",
            model=r"\ReflectanceFeed",
        ),
        _Row(
            parameter="Grating efficiency",
            draft=r"30\%",
            model=r"\EfficiencyGrating",
        ),
        _Row(
            parameter="Filter transmission",
            draft=r"13\%",
            model=r"\TransmissionFilter",
        ),
        _Row(
            parameter="Detector absorbance",
            draft="not given",
            model=r"\AbsorbanceSensor",
        ),
        _Row(
            parameter="Charge collection",
            draft="not given",
            model=r"\ChargeCollection",
        ),
        _Row(
            parameter="Quantum efficiency",
            draft=r"20\%",
            model=r"\QuantumEfficiency",
        ),
        _Row(
            parameter="Effective area",
            draft=r"0.0204\,mm$^2$",
            model=r"\AreaEffectiveMin\ to \AreaEffectiveMax",
        ),
        _Row(
            parameter="Quantum yield",
            draft="1",
            model=r"\QuantumYieldMin\ to \QuantumYieldMax",
        ),
    ]


def throughput() -> str:
    """
    The LaTeX of a table comparing the terms of the effective area in the
    draft with those of the model.
    """
    lines = [
        r"\begin{table}[!ht]",
        r"\centering",
        r"\caption{",
        r"Terms of the effective area in Table~4 of the draft of",
        rf"{date_draft}, beside those of the model, averaged over the",
        r"sampled wavelengths of every channel, except for the effective area",
        r"and the quantum yield, which are given as their range.",
        r"The effective area of the model includes the absorbance of the",
        r"detector but not its charge collection efficiency or its quantum",
        r"yield, which enter the response instead.",
        r"The quantum efficiency of the model is the product of the",
        r"absorbance and the charge collection efficiency, the fraction of the",
        r"charge liberated in the detector which reaches a pixel.",
        r"The quantum yield of the draft is from its Table~5.",
        r"}",
        rf"\label{{{label_throughput}}}",
        r"\begin{tabular}{lll}",
        r"\hline",
        r"Term & Draft & Model \\",
        r"\hline",
    ]
    for row in _rows_throughput():
        lines.append(" & ".join([row.parameter, row.draft, row.model]) + r" \\")
    lines += [
        r"\hline",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


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
        r"The grating of the model is the flight grating, whose ruled area and",
        r"ruling density are as Zeiss measured them \citep{Stock2023}.",
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
