import dataclasses
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import astropy.visualization
import aastex
import named_arrays as na
import furst
from .. import _style

__all__ = [
    "layout",
]

_clearance_entrance = 100 * u.mm
"""
How far beyond the grating the sunlight is drawn entering the instrument.

The Sun is at infinity, so the rays are drawn from wherever the model puts
the solar disk, and the design puts it a breadboard length behind the
grating, which would leave the optics stranded at one end of a very wide
drawing. Moving it changes only where the incoming rays start being drawn.
"""

_color_rays = "tab:blue"
"""The color of the sunlight traced through the instrument."""

_margin = 40 * u.mm
"""The space left around the optics on each side of the drawing."""

_height = 2.4
"""The height of the figure in inches."""

_num_pupil = na.Cartesian2dVectorArray(3, 1)
"""
How many rays are traced across the pupil.

Three across the width of the grating, so that the beam reads as a beam,
and one along its height, since the drawing is a top view.
"""


def _layout_instrument() -> furst.instruments.Instrument:
    """
    The instrument as drawn, with the sunlight entering just behind the
    grating and only enough rays to show its path.
    """
    result = furst.instruments.design(
        num_wavelength=3,
        num_field=1,
        num_pupil=1,
    )
    result.pupil = dataclasses.replace(result.pupil, num=_num_pupil)

    origin = na.Cartesian3dVectorArray() * u.mm
    z_grating = result.grating.transformation(origin).z
    z_entrance = z_grating - _clearance_entrance

    result.source = dataclasses.replace(
        result.source,
        translation=dataclasses.replace(
            result.source.translation,
            z=z_entrance - _clearance_entrance / 2,
        ),
    )
    result.front_aperture = dataclasses.replace(
        result.front_aperture,
        translation=dataclasses.replace(
            result.front_aperture.translation,
            z=z_entrance,
        ),
    )

    return result


def _rowland_circle(
    instrument: furst.instruments.Instrument,
) -> na.Cartesian3dVectorArray:
    """The Rowland circle of the instrument, in the global coordinate system."""
    radius = instrument.grating.rowland_radius
    angle = na.linspace(0, 360, axis="angle", num=1001) * u.deg
    return na.Cartesian3dVectorArray(
        x=radius * np.sin(angle),
        y=0 * radius,
        z=radius * np.cos(angle),
    )


def layout() -> aastex.FigureStar:
    """
    The optical layout of FURST, drawn from the instrument model.

    A top view, looking down on the optical table, with sunlight entering
    from the left and three wavelengths traced through each of the seven
    channels.
    """
    instrument = _layout_instrument()
    origin = na.Cartesian3dVectorArray() * u.mm

    with astropy.visualization.quantity_support(), plt.rc_context(_style.rc):
        fig, ax = plt.subplots(
            figsize=(aastex.text_width_inches, _height),
            constrained_layout=True,
        )

        instrument.system.plot(
            ax=ax,
            components=("z", "x"),
            color="black",
            linewidth=0.5,
            kwargs_rays=dict(
                color=_color_rays,
                linewidth=0.3,
            ),
        )

        circle = _rowland_circle(instrument)
        na.plt.plot(
            circle.z,
            circle.x,
            ax=ax,
            axis="angle",
            color="gray",
            linestyle="--",
            linewidth=0.5,
            zorder=-10,
        )

        # the extent of the optics, which the Rowland circle is clipped to
        position_feed = instrument.feed_optic.transformation(origin)
        position_grating = instrument.grating.transformation(origin)
        position_sensor = instrument.camera.sensor.transformation(origin)

        x_max = position_feed.x.max() + _margin
        x_min = min(position_grating.x.min(), position_sensor.x.min()) - _margin
        ax.set_ylim(x_min.to_value(u.mm), x_max.to_value(u.mm))
        ax.set_aspect("equal")

        ax.set_xlabel(f"$z$ ({ax.get_xlabel()})")
        ax.set_ylabel(f"$x$ ({ax.get_ylabel()})")

        _annotate(ax, instrument)

    result = aastex.FigureStar("fig:layout", position="!ht")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\textwidth"),
    )
    plt.close(fig)
    result.add_caption(
        aastex.NoEscape(
            r"""
The optical layout of FURST, seen from above the optical table.
Sunlight enters from the left and is reflected by one of seven convex
cylindrical feed optics, each of which forms a virtual image of the Sun on
the Rowland circle (dashed), narrower than a pixel of the detector.
The concave diffraction grating, at the far side of the circle, disperses
the light and focuses it back onto the circle at the detector.
Each feed optic illuminates the grating at a different angle of incidence,
so each channel places a different band of the spectrum on the detector.
Three wavelengths are traced through each channel."""
        )
    )

    return result


def _annotate(
    ax: plt.Axes,
    instrument: furst.instruments.Instrument,
) -> None:
    """Label the parts of the instrument the caption talks about."""
    origin = na.Cartesian3dVectorArray() * u.mm

    position_feed = instrument.feed_optic.transformation(origin)
    position_grating = instrument.grating.transformation(origin)
    position_sensor = instrument.camera.sensor.transformation(origin)
    radius_rowland = instrument.grating.rowland_radius

    labels = [
        (
            "feed optics",
            position_feed.z.mean() + 20 * u.mm,
            position_feed.x.mean(),
            dict(ha="left", va="center"),
        ),
        (
            "grating",
            position_grating.z.mean() - 15 * u.mm,
            position_grating.x.mean(),
            dict(ha="right", va="center"),
        ),
        (
            "detector",
            position_sensor.z.mean() + 15 * u.mm,
            position_sensor.x.mean(),
            dict(ha="left", va="center"),
        ),
        (
            "Rowland circle",
            0 * u.mm,
            radius_rowland - 5 * u.mm,
            dict(ha="center", va="top", color="gray"),
        ),
    ]

    for text, z, x, kwargs in labels:
        ax.text(
            na.as_named_array(z).ndarray.to_value(u.mm),
            na.as_named_array(x).ndarray.to_value(u.mm),
            text,
            fontsize=7,
            **kwargs,
        )
