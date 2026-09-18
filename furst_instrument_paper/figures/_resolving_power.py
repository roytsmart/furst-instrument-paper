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

_height = 2.6
"""The height of the figure in inches."""

_color_requirement = "gray"
"""The color of the line marking the resolving power requirement."""


def resolving_power() -> aastex.Figure:
    """
    The resolving power of every channel at the traced wavelengths.
    """
    instrument = furst_instrument_paper.instrument()
    performance = furst_instrument_paper.performance()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, ax = plt.subplots(
            figsize=(aastex.column_width_inches, _height),
            constrained_layout=True,
        )

        ax.axhline(
            resolving_power_required,
            color=_color_requirement,
            linestyle="--",
            linewidth=0.5,
        )

        for i in range(num_channel):
            index = {axis_channel: i}
            na.plt.plot(
                performance.wavelength[index],
                performance.resolving_power[index],
                ax=ax,
                axis=axis_wavelength,
                marker="o",
                label=f"{i + 1}",
            )

        ax.set_xlabel(f"wavelength ({ax.get_xlabel()})")
        ax.set_ylabel("resolving power")
        ax.set_ylim(bottom=0)
        ax.legend(
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
The resolving power of each channel of FURST, computed from a raytrace
of the instrument model.
The line spread function is integrated over the whole solar disk and the
whole pupil, its width includes the width of a pixel, and the resolvable
wavelength difference is taken to be twice that width.
The dashed line marks the requirement of \ensuremath{2 \times 10^4}."""))

    return result
