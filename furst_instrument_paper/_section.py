import re
import furst_instrument_paper
from ._export_figures import figures_latex, figures_performance, figures_response
from ._tables import design_parameters, throughput

__all__ = [
    "section",
    "section_response",
]

label = "sec:opticalPerformance"
"""The label of the section, for the manuscript to refer to."""

label_response = "sec:response"
"""The label of the response section, for the manuscript to refer to."""


def _prose() -> str:
    """
    The text of the section, with every number written as a macro.

    The macros are defined at the top of the exported file, so the text
    follows the instrument model rather than drifting from it.
    """
    return r"""
\subsection{Optical Performance}
\label{sec:opticalPerformance}

The performance of the instrument as it was built and flown was evaluated
by tracing rays through a model of it,
\href{https://furst-optics.readthedocs.io}{\texttt{furst-optics}}
\citep{furstOptics}, built with the open-source
\href{https://optika.readthedocs.io}{\texttt{optika}} raytracing package
\citep{optika}.
The model is shown in Figure~\ref{fig:layout} and its parameters are
listed in Table~\ref{tab:designParameters}.
It places the \NumChannelsWords\ feed optics, the grating, and the detector
on a Rowland circle of radius \RowlandRadius, as the instrument was laid out
for a grating with a radius of curvature of \GratingRadiusLayout.
The flight grating came out with a radius of \GratingRadius, but the
grating and the detector were left where the layout put them, so the model
keeps them there and changes only the curvature of the grating.
Its ruled area is \GratingWidthClear\ wide and \GratingHeightClear\ tall,
with a ruling density of \GratingRulingDensity, as Zeiss measured them for
its final report on the grating \citep{Stock2023}.
The Sun is the field stop of the system and the grating is its pupil stop:
the field of view is the solar disk at its largest apparent size, and every
ray leaving a point on the disk is directed at a point on the ruled area of
the grating.
Each feed optic is a convex cylinder of radius \FeedOpticRadius\ whose clear
aperture subtends \FeedOpticSubtent\ of the cylinder and is \FeedOpticHeight\
tall.

The feed optics illuminate the grating at angles of incidence from
\AngleIncidenceMin\ to \AngleIncidenceMax, and the detector lies
\AngleDiffraction\ from the grating normal on the same side, so that the
shortest wavelengths are observed close to the Littrow configuration.
Each channel therefore places a band about \ChannelBandwidth\ wide on the
detector, and the \NumChannelsWords\ bands together cover \WavelengthMin\ to
\WavelengthMax, with adjacent channels overlapping by at least
\ChannelOverlap\ so that the spectrum can be stitched together.
The dispersion at the detector is \DispersionPerPixel\ per pixel.

A visible-blind filter on a \FilterThickness\ window of magnesium fluoride
sits in front of the detector and moves the focus behind it, and the longer
radius of the flight grating moves it farther still.
As on the bench, the model brings the instrument back into focus by moving
the feed optic array alone: it slides the array \FocusTranslation\ along
the axis of the instrument, which focuses the first channel, and pivots it
\FocusAngle\ about the first feed optic, which focuses the last.

Since the virtual image of the entire Sun formed by a feed optic is
narrower than a pixel, the quantity that governs the spectral resolution is
the disk-integrated line spread function (LSF): the distribution along the
dispersion direction of the light from the whole solar disk and the whole
pupil at a single wavelength.
We compute it by tracing \NumWavelengthTraced\ wavelengths spanning the
detector in each channel, with the solar disk sampled by a stratified random
grid of \NumFieldSamples\ points and the pupil by one of \NumPupilSamples\
points.
The result is shown in Figure~\ref{fig:lsf}: the image of the Sun at each
wavelength is a line about a pixel wide, taller than the detector, and its
profile along the dispersion direction is roughly Gaussian.
We take the width of the LSF to be the standard deviation along the
dispersion direction of the positions of the rays reaching the detector,
added in quadrature with the standard deviation of a uniform distribution
one pixel wide, to account for the finite size of the pixels.
This width is shown in the top panel of Figure~\ref{fig:resolvingPower} and
ranges from \LsfWidthMin\ to \LsfWidthMax\ pixels.
It is largest in the middle channels: since the radius of the flight
grating differs from that of the layout, only the two end channels can be
brought to their best focus, one by each motion of the feed optic array,
and the channels between them sit a little off it.

The resolving power, taken as the wavelength divided by twice the width of
the LSF, is shown in the bottom panel of Figure~\ref{fig:resolvingPower}.
It ranges from \ResolvingPowerMin\ to \ResolvingPowerMax\ over the traced
wavelengths, with a mean of \ResolvingPowerMean, and so exceeds the
requirement of \ensuremath{2 \times 10^4} throughout the bandpass.

Every figure in this section, and every number it takes from the model,
is computed from the instrument model by
\href{https://github.com/roytsmart/furst-instrument-paper}{\texttt{furst-instrument-paper}}
\citep{furstInstrumentPaper}, so that they cannot drift from it.
"""


def section() -> str:
    """
    The LaTeX of the optical performance section, ready to be included in
    the manuscript with ``\\input``.

    The file defines a macro for every number it cites, then gives the text
    of the section, then the table and the figures it refers to.
    """
    variables = [v.dumps() for v in furst_instrument_paper.variables()]

    parts = [
        "% Generated by furst-instrument-paper. Do not edit by hand.",
        "",
        "\n".join(variables),
        "",
        _prose().strip("\n"),
        "",
        design_parameters(),
        "",
        figures_latex(figures_performance()),
    ]
    return "\n".join(parts) + "\n"


def _prose_response() -> str:
    """
    The text of the response section, with every number written as a
    macro.
    """
    return r"""
\subsection{Response}
\label{sec:response}

The response of the instrument is the rate at which it records electrons
for a given irradiance at its entrance.
We compute it from the same model of the instrument and show it, with each
of its factors, in Figure~\ref{fig:response}: the efficiency of each optic
the light meets, and the quantum efficiency of the detector.
Each is computed one channel at a time, since each channel meets the grating
at its own angle, and the neighboring channels agree where their bands
overlap.

The feed optics reflect \ReflectanceFeed\ of the light on average, as
measured on witness samples coated alongside them.
The grating sends \EfficiencyGrating\ of it into the first order: the
reflectance Zeiss measured on a test piece coated with it, times the
efficiency Zeiss computed for grooves of the profile it measured on the
flight grating \citep{Stock2023}, at the angle of incidence of each channel.
The visible-blind filter, as measured on its witness sample, transmits
\TransmissionFilter\ on average, and less toward Lyman~\ensuremath{\alpha}.

The quantum efficiency of the detector, in electrons per incident photon,
is the product of three factors: the fraction of the photons absorbed in
its silicon, \AbsorbanceSensor\ on average; the fraction of the charge they
liberate which reaches a pixel, its charge collection efficiency,
\ChargeCollection; and the number of electron-hole pairs each absorbed
photon liberates, its quantum yield, which falls from \QuantumYieldMax\ to
\QuantumYieldMin\ across the bandpass.
We do not correct it for the quantum yield, so it counts electrons rather
than photons, and it ranges from \QuantumEfficiencyMin\ to
\QuantumEfficiencyMax.
It is the least certain of the factors, since the detector is modeled rather
than measured: the charge collection efficiency is that of a model of an
e2v CCD97 fit in part to the measurements of \citet{Heymes2020}, not of the
CCD230-42 which flew, and the quantum yield is the model of
\citet{Ramanathan2020}, which is fit to measurements only at photon
energies below 8\,eV, longward of 155\,nm.

The response, in the bottom panel of Figure~\ref{fig:response}, is the
product of these factors and the area the instrument collects light from,
divided by the energy of a photon.
That area, \AreaCollecting, is set by the layout alone, and is small
because each convex feed optic spreads the light it reflects over a wide
fan, of which the grating intercepts only a small part.
Multiplied by the irradiance of a spectral line in
\ensuremath{\mathrm{erg\,cm^{-2}\,s^{-1}}}, the response gives the
electrons per second that the line deposits on the detector.
It rises steeply across the first channel, from \ResponseMin, as the
transmission of the filter and the absorbance of the detector both fall
toward Lyman~\ensuremath{\alpha}, and reaches \ResponseMax\ in the middle of
the bandpass.
Since the quantum yield falls almost in proportion to the energy of a
photon, the detector records nearly the same charge for each unit of energy
it absorbs, and beyond the first channel the response follows the product
of the efficiencies of the three optics.
Table~\ref{tab:throughput} sets each of these factors beside the estimates
in Table~4 of the draft.
"""


def section_response() -> str:
    """
    The LaTeX of the response section, ready to be included in the
    manuscript with ``\\input``.

    Like :func:`section`, the file defines a macro for every number it
    cites, then gives the text of the section, then the table and the
    figure it refers to.
    """
    variables = [v.dumps() for v in furst_instrument_paper.variables_response()]

    parts = [
        "% Generated by furst-instrument-paper. Do not edit by hand.",
        "",
        "\n".join(variables),
        "",
        _prose_response().strip("\n"),
        "",
        throughput(),
        "",
        figures_latex(figures_response()),
    ]
    return "\n".join(parts) + "\n"


def _names_defined(latex: str) -> set[str]:
    """The names of the macros a piece of LaTeX defines."""
    return set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", latex))


def macros_undefined(latex: str) -> set[str]:
    """
    The macros a piece of LaTeX cites without defining.

    Used by the tests to make sure the text does not refer to a number the
    model has not supplied. Only capitalized names are checked, which is how
    every variable of this package is named and how no LaTeX primitive is.
    """
    defined = _names_defined(latex)
    cited = set(re.findall(r"\\([A-Z][A-Za-z]+)", latex))
    return cited - defined
