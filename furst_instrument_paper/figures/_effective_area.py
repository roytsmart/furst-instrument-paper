import matplotlib.pyplot as plt
import astropy.units as u
import astropy.visualization
import aastex
import named_arrays as na
import furst_instrument_paper
from .._instrument import axis_channel, axis_wavelength
from .. import _style

__all__ = [
    "effective_area",
]

_height = 4.4
"""The height of the figure in inches."""

_unit_area = u.mm**2
"""The unit the effective area is plotted in, the unit of Table 4 of the draft."""


def effective_area() -> aastex.Figure:
    """
    The effective area and the response of every channel against
    wavelength, one above the other.
    """
    instrument = furst_instrument_paper.instrument()
    radiometry = furst_instrument_paper.radiometry()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]

    area = radiometry.area_effective.to(_unit_area)
    response = radiometry.response

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, (ax_area, ax_response) = plt.subplots(
            nrows=2,
            sharex=True,
            figsize=(aastex.column_width_inches, _height),
            constrained_layout=True,
        )

        for i in range(num_channel):
            index = {axis_channel: i}
            wavelength = radiometry.wavelength[index]
            na.plt.plot(
                wavelength,
                area[index],
                ax=ax_area,
                axis=axis_wavelength,
            )
            na.plt.plot(
                wavelength,
                response[index],
                ax=ax_response,
                axis=axis_wavelength,
                label=f"{i + 1}",
            )

        ax_area.set_ylabel(f"effective area ({_unit_area:latex_inline})")
        ax_area.set_ylim(bottom=0)

        ax_response.set_xlabel(f"wavelength ({ax_response.get_xlabel()})")
        ax_response.set_ylabel(r"response ($\mathrm{e^{-}\,cm^{2}\,erg^{-1}}$)")
        ax_response.set_ylim(bottom=0)
        ax_response.legend(
            title="channel",
            ncols=2,
            loc="lower right",
        )

    result = aastex.Figure("fig:effectiveArea", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\columnwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The throughput of each channel of FURST, from the instrument model.
Top: the effective area, averaged over the solar disk, including the
reflectance of the feed optics, the efficiency of the grating, the
transmission of the visible-blind filter, and the absorbance of the
detector.
Bottom: the response, the effective area times the charge collection
efficiency and the quantum yield of the detector, divided by the energy of
a photon.
Multiplied by the irradiance of a spectral line in
\ensuremath{\mathrm{erg\,cm^{-2}\,s^{-1}}}, it gives the electrons per
second that the line deposits on the detector."""))

    return result
