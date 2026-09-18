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

_margin = 50 * u.mm
"""The space left around the optics on each side of the drawing."""

_gap = 8
"""The space, in millimeters, between a label and the outline it names."""

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


def _extent_x(
    instrument: furst.instruments.Instrument,
) -> tuple[na.AbstractScalar, na.AbstractScalar]:
    """
    The least and greatest horizontal position of any optic in the drawing.

    Read from the outlines of the apertures rather than from their centers,
    so that the grating, which is wide, is not cut off at its edge.
    """
    components = (
        instrument.feed_optic,
        instrument.grating,
        instrument.camera.sensor,
    )
    bounds = [_bounds(component) for component in components]
    x_min = min(b.x_min for b in bounds)
    x_max = max(b.x_max for b in bounds)
    return x_min * u.mm, x_max * u.mm


def _millimeters(value: u.Quantity | na.AbstractScalar) -> float:
    """The value in millimeters, as a plain number for :mod:`matplotlib`."""
    return float(na.as_named_array(value).ndarray.to_value(u.mm))


def layout() -> aastex.FigureStar:
    """
    The optical layout of FURST, drawn from the instrument model.

    A top view, looking down on the optical table, with sunlight entering
    from the left and three wavelengths traced through each of the seven
    channels.
    """
    instrument = _layout_instrument()

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
        x_min, x_max = _extent_x(instrument)
        ax.set_ylim(
            _millimeters(x_min - _margin),
            _millimeters(x_max + _margin),
        )
        ax.set_aspect("equal")

        ax.set_xlabel(f"$z$ ({ax.get_xlabel()})")
        ax.set_ylabel(f"$x$ ({ax.get_ylabel()})")

        _annotate(ax, instrument)

    result = aastex.FigureStar("fig:layout", position="!ht")
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\textwidth"),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The optical layout of FURST, seen from above the optical table.
Sunlight enters from the left and is reflected by one of seven convex
cylindrical feed optics, each of which forms a virtual image of the Sun on
the Rowland circle (dashed), narrower than a pixel of the detector.
The concave diffraction grating, at the far side of the circle, disperses
the light and focuses it back onto the circle at the detector.
Each feed optic illuminates the grating at a different angle of incidence,
so each channel places a different band of the spectrum on the detector.
Three wavelengths are traced through each channel."""))

    return result


def _annotate(
    ax: plt.Axes,
    instrument: furst.instruments.Instrument,
) -> None:
    """
    Label the parts of the instrument the caption talks about.

    Every label sits just outside the outline of its part, on the side away
    from the light: above the feed optics, whose incoming beam is below the
    topmost of them, and below the grating and the detector, whose beams
    arrive from above.
    """
    feed = _bounds(instrument.feed_optic)
    grating = _bounds(instrument.grating)
    sensor = _bounds(instrument.camera.sensor)

    # the Rowland circle is labelled on its arc between the detector and the
    # feed optics, where nothing else is drawn
    radius_rowland = _millimeters(instrument.grating.rowland_radius)
    x_circle = (feed.x_min + sensor.x_max) / 2
    z_circle = np.sqrt(np.square(radius_rowland) - np.square(x_circle))

    labels = [
        (
            "feed optics",
            (feed.z_min + feed.z_max) / 2,
            feed.x_max + _gap,
            dict(ha="center", va="bottom"),
        ),
        (
            "grating",
            (grating.z_min + grating.z_max) / 2,
            grating.x_min - _gap,
            dict(ha="center", va="top"),
        ),
        (
            "detector",
            (sensor.z_min + sensor.z_max) / 2,
            sensor.x_min - _gap,
            dict(ha="center", va="top"),
        ),
        (
            "Rowland circle",
            z_circle - _gap,
            x_circle,
            dict(ha="right", va="center", color="gray"),
        ),
    ]

    for text, z, x, kwargs in labels:
        ax.text(
            z,
            x,
            text,
            fontsize=7,
            **kwargs,
        )


@dataclasses.dataclass(frozen=True)
class _Bounds:
    """The extent of the outline of an optic in the drawing, in millimeters."""

    x_min: float
    x_max: float
    z_min: float
    z_max: float


def _bounds(component) -> _Bounds:
    """
    The extent of the outline of an optic, read from its aperture.

    The mechanical aperture is used where the optic has one, since that is
    the outline drawn, and the clear aperture otherwise.
    """
    surface = component.surface
    aperture = surface.aperture_mechanical
    if aperture is None:
        aperture = surface.aperture
    wire = surface.transformation(aperture.wire())
    return _Bounds(
        x_min=_millimeters(wire.x.min()),
        x_max=_millimeters(wire.x.max()),
        z_min=_millimeters(wire.z.min()),
        z_max=_millimeters(wire.z.max()),
    )
