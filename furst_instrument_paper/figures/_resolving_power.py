import matplotlib.pyplot as plt
import astropy.visualization
import aastex
import named_arrays as na
import furst_instrument_paper
from .._instrument import axis_channel, axis_wavelength
from .._performance import resolving_power_required
from .. import _style

__all__ = [
    "resolving_power",
]

_height = 4.4
"""The height of the figure in inches."""

_color_requirement = "gray"
"""The color of the line marking the resolving power requirement."""


def resolving_power() -> aastex.Figure:
    """
    The width of the line spread function and the resolving power of every
    channel at the traced wavelengths, one above the other against
    wavelength.
    """
    instrument = furst_instrument_paper.instrument()
    performance = furst_instrument_paper.performance()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, (ax_width, ax_power) = plt.subplots(
            nrows=2,
            sharex=True,
            figsize=(aastex.column_width_inches, _height),
            constrained_layout=True,
        )

        ax_power.axhline(
            resolving_power_required,
            color=_color_requirement,
            linestyle="--",
            linewidth=0.5,
        )

        for i in range(num_channel):
            index = {axis_channel: i}
            wavelength = performance.wavelength[index]
            na.plt.plot(
                wavelength,
                performance.width[index],
                ax=ax_width,
                axis=axis_wavelength,
                marker="o",
            )
            na.plt.plot(
                wavelength,
                performance.resolving_power[index],
                ax=ax_power,
                axis=axis_wavelength,
                marker="o",
                label=f"{i + 1}",
            )

        ax_width.set_ylabel(f"LSF width ({ax_width.get_ylabel()})")
        ax_width.set_ylim(bottom=0)

        ax_power.set_xlabel(f"wavelength ({ax_power.get_xlabel()})")
        ax_power.set_ylabel("resolving power")
        ax_power.set_ylim(bottom=0)
        ax_power.legend(
            title="channel",
            ncols=2,
            loc="lower right",
        )

    result = aastex.Figure("fig:resolvingPower", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\columnwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The spectral resolution of each channel of FURST at the traced wavelengths,
computed from a raytrace of the instrument model.
Top: the width of the disk-integrated line spread function, the standard
deviation of the positions of the rays along the dispersion direction,
added in quadrature with the standard deviation of a uniform distribution
one pixel wide.
Bottom: the resolving power, taking the resolvable wavelength difference to
be twice that width.
The dashed line marks the requirement of \ensuremath{2 \times 10^4}."""))

    return result
