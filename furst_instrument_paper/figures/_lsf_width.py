import matplotlib.pyplot as plt
import astropy.visualization
import aastex
import named_arrays as na
import furst_instrument_paper
from .._instrument import axis_channel, axis_wavelength
from .. import _style

__all__ = [
    "lsf_width",
]

_height = 2.6
"""The height of the figure in inches."""


def lsf_width() -> aastex.Figure:
    """
    The width of the disk-integrated line spread function of every channel
    at the traced wavelengths.
    """
    instrument = furst_instrument_paper.instrument()
    performance = furst_instrument_paper.performance()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, ax = plt.subplots(
            figsize=(aastex.column_width_inches, _height),
            constrained_layout=True,
        )

        for i in range(num_channel):
            index = {axis_channel: i}
            na.plt.plot(
                performance.wavelength[index],
                performance.width[index],
                ax=ax,
                axis=axis_wavelength,
                marker="o",
                label=f"{i + 1}",
            )

        ax.set_xlabel(f"wavelength ({ax.get_xlabel()})")
        ax.set_ylabel(f"LSF width ({ax.get_ylabel()})")
        ax.set_ylim(bottom=0)
        ax.legend(
            title="channel",
            ncols=2,
            loc="lower right",
        )

    result = aastex.Figure("fig:lsfWidth", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\columnwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The width of the disk-integrated line spread function of each channel of
FURST at the traced wavelengths: the standard deviation of the positions of
the rays along the dispersion direction, added in quadrature with the
standard deviation of a uniform distribution one pixel wide."""))

    return result
