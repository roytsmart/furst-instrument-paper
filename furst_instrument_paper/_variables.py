import numpy as np
import astropy.units as u
import aastex
import named_arrays as na
import furst_instrument_paper
from ._instrument import axis_channel, axis_wavelength

__all__ = [
    "variables",
]


def _angle_from_normal(
    position: na.AbstractCartesian3dVectorArray,
    grating,
) -> na.AbstractScalar:
    """
    The angle between the normal of the grating and the direction to a
    point, as seen from the center of the grating.
    """
    position = grating.transformation.inverse(position)
    return np.arctan2(position.xy.length, np.abs(position.z)).to(u.deg)


def variables() -> list[aastex.Variable]:
    """
    A LaTeX variable for every numeric quantity the prose cites.

    Each is a ``\\newcommand`` taking its value from the instrument model,
    so that the text follows the model instead of drifting from it.
    """
    instrument = furst_instrument_paper.instrument()
    performance = furst_instrument_paper.performance()

    feed_optic = instrument.feed_optic
    grating = instrument.grating
    sensor = instrument.camera.sensor

    origin = na.Cartesian3dVectorArray() * u.mm

    num_channel = feed_optic.rowland_azimuth.shape[axis_channel]

    wavelength_min = instrument.wavelength_min.to(u.nm)
    wavelength_max = instrument.wavelength_max.to(u.nm)

    # the overlap between each channel and the next one up in wavelength
    index_lower = {axis_channel: slice(None, ~0)}
    index_upper = {axis_channel: slice(1, None)}
    overlap = wavelength_max[index_lower] - wavelength_min[index_upper]

    angle_incidence = _angle_from_normal(
        position=feed_optic.transformation_image(origin),
        grating=grating,
    )
    angle_diffraction = _angle_from_normal(
        position=sensor.transformation(origin),
        grating=grating,
    )

    width_sensor = (sensor.num_pixel_active * sensor.width_pixel).to(u.mm)

    ruling_density = (1 / grating.rulings.spacing).to(1 / u.mm)

    return [
        aastex.Variable("NumChannels", num_channel),
        aastex.Variable("WavelengthMin", wavelength_min.min().ndarray.round(1)),
        aastex.Variable("WavelengthMax", wavelength_max.max().ndarray.round(1)),
        aastex.Variable(
            "ChannelBandwidth",
            (wavelength_max - wavelength_min).mean().ndarray.round(1),
        ),
        aastex.Variable("ChannelOverlap", overlap.min().ndarray.round(1)),
        aastex.Variable("RowlandRadius", grating.rowland_radius.round(0)),
        aastex.Variable("GratingRadius", np.abs(grating.sag.radius).round(0)),
        aastex.Variable("GratingRulingDensity", ruling_density.round(0)),
        aastex.Variable("GratingWidthClear", grating.width_clear.x.round(0)),
        aastex.Variable("GratingHeightClear", grating.width_clear.y.round(1)),
        aastex.Variable("FeedOpticRadius", feed_optic.radius),
        aastex.Variable("FeedOpticHeight", feed_optic.aperture_height.ndarray.round(1)),
        aastex.Variable("FeedOpticSubtent", feed_optic.aperture_subtent),
        aastex.Variable("AngleIncidenceMin", angle_incidence.min().ndarray.round(2)),
        aastex.Variable("AngleIncidenceMax", angle_incidence.max().ndarray.round(2)),
        aastex.Variable("AngleDiffraction", angle_diffraction.ndarray.round(2)),
        aastex.Variable("PixelWidth", sensor.width_pixel),
        aastex.Variable("SensorWidth", width_sensor.x.round(1)),
        aastex.Variable("SensorHeight", width_sensor.y.round(1)),
        aastex.Variable("NumPixelX", int(sensor.num_pixel_active.x)),
        aastex.Variable("NumPixelY", int(sensor.num_pixel_active.y)),
        aastex.Variable(
            "DispersionPerPixel",
            (performance.dispersion.mean().ndarray * sensor.width_pixel)
            .to(u.pm)
            .round(2),
        ),
        aastex.Variable(
            "LsfWidthMin",
            performance.width.min().ndarray.round(2),
        ),
        aastex.Variable(
            "LsfWidthMax",
            performance.width.max().ndarray.round(2),
        ),
        aastex.Variable(
            "ResolvingPowerMin",
            int(np.round(performance.resolving_power.min().ndarray, -2)),
        ),
        aastex.Variable(
            "ResolvingPowerMean",
            int(np.round(performance.resolving_power.mean().ndarray, -2)),
        ),
        aastex.Variable(
            "ResolvingPowerMax",
            int(np.round(performance.resolving_power.max().ndarray, -2)),
        ),
        aastex.Variable(
            "NumWavelengthTraced", performance.wavelength.shape[axis_wavelength]
        ),
    ]
