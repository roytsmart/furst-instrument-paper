import numpy as np
import astropy.units as u
import num2words
import aastex
import named_arrays as na
import furst_instrument_paper
from ._instrument import axis_channel, axis_wavelength, num_field, num_pupil
from ._radiometry import unit_response

__all__ = [
    "variables",
    "variables_response",
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

    # the instrument was laid out for a grating whose radius is the
    # diameter of the Rowland circle, and the flight grating differs from it
    radius_layout = 2 * grating.rowland_radius

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
        aastex.Variable("NumChannelsWords", num2words.num2words(num_channel)),
        aastex.Variable("WavelengthMin", wavelength_min.min().ndarray.round(1)),
        aastex.Variable("WavelengthMax", wavelength_max.max().ndarray.round(1)),
        aastex.Variable(
            "ChannelBandwidth",
            (wavelength_max - wavelength_min).mean().ndarray.round(1),
        ),
        aastex.Variable("ChannelOverlap", overlap.min().ndarray.round(1)),
        aastex.Variable("RowlandRadius", grating.rowland_radius.round(0)),
        aastex.Variable("GratingRadiusLayout", radius_layout.round(0)),
        aastex.Variable("GratingRadius", np.abs(grating.sag.radius).round(0)),
        aastex.Variable("GratingRulingDensity", ruling_density.round(0)),
        aastex.Variable("GratingWidthClear", grating.width_clear.x.round(1)),
        aastex.Variable("GratingHeightClear", grating.width_clear.y.round(1)),
        aastex.Variable("FilterThickness", instrument.filter.thickness.round(3)),
        aastex.Variable(
            "FocusTranslation",
            na.as_named_array(feed_optic.translation_focus).ndarray.round(1),
        ),
        aastex.Variable(
            "FocusAngle",
            np.abs(na.as_named_array(feed_optic.angle_focus).ndarray).round(2),
        ),
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
        # the widths are cited in pixels by the prose, so they are written
        # as plain numbers with two decimals
        aastex.Variable(
            "LsfWidthMin",
            _decimals(performance.width.min(), u.pix),
        ),
        aastex.Variable(
            "LsfWidthMax",
            _decimals(performance.width.max(), u.pix),
        ),
        aastex.Variable(
            "ResolvingPowerMin",
            _hundreds(performance.resolving_power.min()),
        ),
        aastex.Variable(
            "ResolvingPowerMean",
            _hundreds(performance.resolving_power.mean()),
        ),
        aastex.Variable(
            "ResolvingPowerMax",
            _hundreds(performance.resolving_power.max()),
        ),
        aastex.Variable(
            "NumWavelengthTraced", performance.wavelength.shape[axis_wavelength]
        ),
        aastex.Variable("NumFieldSamples", _grid(num_field)),
        aastex.Variable("NumPupilSamples", _grid(num_pupil)),
    ]


def variables_response() -> list[aastex.Variable]:
    """
    A LaTeX variable for every numeric quantity the response section cites.

    Kept apart from :func:`variables`, since each exported file defines the
    macros it cites, and no name may be defined by both.

    The efficiencies are cited as their means over the sampled wavelengths
    of every channel, and the effective area, the quantum yield, and the
    response as their ranges.
    """
    radiometry = furst_instrument_paper.radiometry()

    unit_yield = u.electron / u.ph
    area_electrons = radiometry.area_effective_electrons

    return [
        aastex.Variable(
            "AreaCollecting",
            radiometry.area_collecting.mean().ndarray.round(1),
        ),
        aastex.Variable("ReflectanceFeed", _percent(radiometry.reflectance_feed)),
        aastex.Variable("EfficiencyGrating", _percent(radiometry.efficiency_grating)),
        aastex.Variable("TransmissionFilter", _percent(radiometry.transmission_filter)),
        aastex.Variable("AbsorbanceSensor", _percent(radiometry.absorbance)),
        aastex.Variable(
            "ChargeCollection",
            _decimals(radiometry.charge_collection.mean(), u.one),
        ),
        aastex.Variable(
            "QuantumYieldMin",
            _decimals(radiometry.quantum_yield.min(), unit_yield, num=1),
        ),
        aastex.Variable(
            "QuantumYieldMax",
            _decimals(radiometry.quantum_yield.max(), unit_yield, num=1),
        ),
        aastex.Variable(
            "QuantumEfficiency",
            _per_photon(radiometry.quantum_efficiency.mean()),
        ),
        aastex.Variable(
            "QuantumEfficiencyMin",
            _per_photon(radiometry.quantum_efficiency.min()),
        ),
        aastex.Variable(
            "QuantumEfficiencyMax",
            _per_photon(radiometry.quantum_efficiency.max()),
        ),
        aastex.Variable("AreaEffectiveMin", area_electrons.min().ndarray.round(3)),
        aastex.Variable("AreaEffectiveMax", area_electrons.max().ndarray.round(3)),
        aastex.Variable("ResponseMin", _response(radiometry.response.min())),
        aastex.Variable("ResponseMax", _response(radiometry.response.max())),
    ]


def _decimals(value: na.AbstractScalar, unit: u.UnitBase, num: int = 2) -> str:
    """A quantity as a plain number in the given unit, to `num` decimals."""
    return f"{na.as_named_array(value).ndarray.to_value(unit):.{num}f}"


def _hundreds(value: na.AbstractScalar) -> str:
    """A large dimensionless number rounded to the hundreds, thousands separated."""
    result = int(np.round(na.as_named_array(value).ndarray.to_value(u.one), -2))
    return f"{result:,}"


def _percent(value: na.AbstractScalar) -> str:
    """The mean of a dimensionless fraction, as a whole percentage."""
    mean = na.as_named_array(value).mean().ndarray.to_value(u.one)
    return aastex.NoEscape(rf"{100 * mean:.0f}\%")


def _per_photon(value: na.AbstractScalar) -> str:
    """A quantum efficiency, in electrons per photon to two decimals."""
    value = na.as_named_array(value).ndarray.to_value(u.electron / u.ph)
    unit = r"\mathrm{e^{-}\,photon^{-1}}"
    return aastex.NoEscape(rf"\ensuremath{{{value:.2f}\,{unit}}}")


def _response(value: na.AbstractScalar) -> str:
    """A response, in scientific notation with two significant figures."""
    value = na.as_named_array(value).ndarray.to_value(unit_response)
    exponent = int(np.floor(np.log10(value)))
    mantissa = value / 10**exponent
    unit = r"\mathrm{e^{-}\,cm^{2}\,erg^{-1}}"
    return aastex.NoEscape(
        rf"\ensuremath{{{mantissa:.1f} \times 10^{{{exponent}}}\,{unit}}}"
    )


def _grid(num: int) -> str:
    """A square grid of samples, written as its side lengths."""
    return aastex.NoEscape(rf"${num} \times {num}$")
