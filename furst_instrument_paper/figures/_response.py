import matplotlib.pyplot as plt
import astropy.units as u
import astropy.visualization
import aastex
import named_arrays as na
import furst_instrument_paper
from .._instrument import axis_channel, axis_wavelength
from .._radiometry import unit_response
from .. import _style

__all__ = [
    "response",
]

_height = 5.4
"""The height of the figure in inches."""

_colors_optics = {
    "feed optic": "tab:blue",
    "grating": "tab:orange",
    "filter": "tab:green",
}
"""The color of the efficiency of each optic."""

_color_detector = "black"
"""The color of the quantum efficiency of the detector and of the response."""


def response() -> aastex.Figure:
    """
    The efficiency of each optic, the quantum efficiency of the detector,
    and the response of the instrument, one above the other against
    wavelength.

    Each quantity is drawn one channel at a time, since each channel meets
    the grating at its own angle, so that the segments of neighboring
    channels overlap where their bands do.
    """
    instrument = furst_instrument_paper.instrument()
    radiometry = furst_instrument_paper.radiometry()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]

    efficiencies = {
        "feed optic": radiometry.reflectance_feed,
        "grating": radiometry.efficiency_grating,
        "filter": radiometry.transmission_filter,
    }
    unit_efficiency = u.electron / u.ph

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, (ax_optics, ax_detector, ax_response) = plt.subplots(
            nrows=3,
            sharex=True,
            figsize=(aastex.column_width_inches, _height),
            constrained_layout=True,
        )

        for i in range(num_channel):
            index = {axis_channel: i}
            wavelength = radiometry.wavelength[index]
            for name, efficiency in efficiencies.items():
                na.plt.plot(
                    wavelength,
                    efficiency[index],
                    ax=ax_optics,
                    axis=axis_wavelength,
                    color=_colors_optics[name],
                    # one legend entry for each optic, not for each channel
                    label=name if i == 0 else None,
                )
            na.plt.plot(
                wavelength,
                radiometry.quantum_efficiency[index].to(unit_efficiency),
                ax=ax_detector,
                axis=axis_wavelength,
                color=_color_detector,
            )
            na.plt.plot(
                wavelength,
                radiometry.response[index].to(unit_response),
                ax=ax_response,
                axis=axis_wavelength,
                color=_color_detector,
            )

        ax_optics.set_ylabel("efficiency")
        ax_optics.set_ylim(0, 1)
        ax_optics.legend(ncols=3, loc="upper center")

        ax_detector.set_ylabel(r"quantum efficiency ($\mathrm{e^{-}\,photon^{-1}}$)")
        ax_detector.set_ylim(bottom=0)

        ax_response.set_xlabel(f"wavelength ({ax_response.get_xlabel()})")
        ax_response.set_ylabel(r"response ($\mathrm{e^{-}\,cm^{2}\,erg^{-1}}$)")
        ax_response.set_ylim(bottom=0)

    result = aastex.Figure("fig:response", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\columnwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The response of FURST and its factors, from the instrument model, drawn one
channel at a time.
Top: the reflectance of the feed optics, the first-order efficiency of the
grating at the angle of incidence of each channel, and the transmission of
the visible-blind filter.
Middle: the quantum efficiency of the detector, in electrons per incident
photon, the product of its absorbance, its charge collection efficiency,
and its quantum yield.
Bottom: the response, the electrons recorded for each erg per square
centimeter reaching the instrument, averaged over the solar disk.
Multiplied by the irradiance of a spectral line in
\ensuremath{\mathrm{erg\,cm^{-2}\,s^{-1}}}, it gives the electrons per
second that the line deposits on the detector."""))

    return result
