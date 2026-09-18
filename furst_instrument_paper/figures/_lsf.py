import matplotlib.colors
import matplotlib.lines
import matplotlib.pyplot as plt
import astropy.units as u
import astropy.visualization
import aastex
import named_arrays as na
import furst_instrument_paper
from .._instrument import axis_channel, axis_wavelength, axis_field, axis_pupil
from .. import _style

__all__ = [
    "lsf",
]

_height = 3.9
"""The height of the figure in inches."""

_axis_row = "row"
"""The logical axis of the two rows of panels."""

_bins_x = 21
"""The number of bins across the dispersion direction in the images."""

_bins_y = 21
"""The number of bins along the height of the detector in the images."""

_bins_profile = 41
"""The number of bins across the dispersion direction in the profiles."""

_halfwidth_x = 1 * u.pix
"""How far either side of the mean position the panels extend."""

_halfwidth_y = 8 * u.mm
"""How far either side of the center of the detector the images extend."""

_cmap = "viridis"
"""The colormap distinguishing the traced wavelengths in the profiles."""


def lsf() -> aastex.FigureStar:
    """
    The disk-integrated line spread function of every channel.

    The top row shows its two-dimensional form at the central traced
    wavelength of each channel, and the bottom row its profile along the
    dispersion direction at every traced wavelength.
    """
    instrument = furst_instrument_paper.instrument()
    performance = furst_instrument_paper.performance()

    num_channel = instrument.feed_optic.rowland_azimuth.shape[axis_channel]
    num_wavelength = performance.wavelength.shape[axis_wavelength]

    axes_disk = axis_field + axis_pupil

    index_center = {axis_wavelength: num_wavelength // 2}

    image = na.histogram2d(
        performance.dx[index_center],
        performance.position_y[index_center],
        bins={"lsf_x": _bins_x, "lsf_y": _bins_y},
        axis=axes_disk,
        weights=performance.weight[index_center],
        min=na.Cartesian2dVectorArray(-_halfwidth_x, -_halfwidth_y),
        max=na.Cartesian2dVectorArray(+_halfwidth_x, +_halfwidth_y),
    )

    profile = na.histogram(
        performance.dx,
        bins={"lsf_x": _bins_profile},
        axis=axes_disk,
        weights=performance.weight,
        min=-_halfwidth_x,
        max=+_halfwidth_x,
    )

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, axs = na.plt.subplots(
            axis_rows=_axis_row,
            axis_cols=axis_channel,
            nrows=2,
            ncols=num_channel,
            sharex=True,
            sharey="row",
            # the first row at the top, so the images sit above the profiles
            origin="upper",
            figsize=(aastex.text_width_inches, _height),
            constrained_layout=True,
        )
        axs_image = axs[{_axis_row: 0}]
        axs_profile = axs[{_axis_row: 1}]

        na.plt.pcolormesh(
            C=image,
            ax=axs_image,
        )

        # The traced wavelengths differ from channel to channel, but their
        # offsets from the center of the channel are nearly the same in every
        # channel, so the legend names each color by that offset.
        offset = performance.wavelength - performance.wavelength.mean(axis_wavelength)
        offset = offset.mean(axis_channel)

        colormap = plt.get_cmap(_cmap)
        handles = []
        for j in range(num_wavelength):
            # the color is passed as a string, since named_arrays would
            # otherwise try to broadcast the tuple over the channels
            color = matplotlib.colors.to_hex(colormap(j / max(num_wavelength - 1, 1)))
            na.plt.stairs(
                profile.inputs,
                profile.outputs[{axis_wavelength: j}],
                ax=axs_profile,
                axis="lsf_x",
                color=color,
                linewidth=0.7,
            )
            value = offset[{axis_wavelength: j}].ndarray
            # adding zero turns a negative zero into a plain one
            value = round(value.value, 1) + 0.0
            label = f"{value:+.1f}" if value else f"{value:.1f}"
            handles.append(
                matplotlib.lines.Line2D(
                    [],
                    [],
                    color=color,
                    label=f"{label} {offset.unit}",
                )
            )

        fig.legend(
            handles=handles,
            title="wavelength offset from the center of the channel",
            loc="outside lower center",
            ncols=num_wavelength,
        )

        for i in range(num_channel):
            ax_image = axs_image[{axis_channel: i}].ndarray
            ax_profile = axs_profile[{axis_channel: i}].ndarray
            ax_image.set_title(f"channel {i + 1}")
            ax_image.set_xlabel(None)
            ax_image.set_ylabel(None)
            ax_profile.set_xlabel(f"$x$ ({_halfwidth_x.unit})")
            ax_profile.set_ylabel(None)

        ax = axs_image[{axis_channel: 0}].ndarray
        ax.set_ylabel(f"$y$ ({_halfwidth_y.unit})")
        axs_profile[{axis_channel: 0}].ndarray.set_ylabel("rays")

    result = aastex.FigureStar("fig:lsf", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\textwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The disk-integrated line spread function of each channel of FURST, from a
raytrace of the instrument model.
Top: the distribution of the rays on the detector at the central traced
wavelength of each channel, with the dispersion direction, \ensuremath{x},
measured in pixels from the mean position of that wavelength and the
height on the detector, \ensuremath{y}, measured from its center.
Bottom: the same distribution summed along the height of the detector, at
every traced wavelength of each channel, from the shortest (dark) to the
longest (light)."""))

    return result
