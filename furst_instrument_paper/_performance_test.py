import astropy.units as u
import named_arrays as na
import furst_instrument_paper
from furst_instrument_paper import _instrument, _performance


def test_performance():
    result = furst_instrument_paper.performance()
    assert isinstance(result, furst_instrument_paper.Performance)

    shape = {
        _instrument.axis_channel: 7,
        _instrument.axis_wavelength: _instrument.num_wavelength,
    }
    assert result.wavelength.shape == shape
    assert result.width.shape == shape
    assert result.resolving_power.shape == shape

    assert na.unit(result.wavelength).is_equivalent(u.nm)
    assert na.unit(result.width).is_equivalent(u.pix)
    assert na.unit(result.dispersion).is_equivalent(u.nm / u.mm)


def test_width():
    """The image of the Sun is narrower than a pixel in every channel."""
    result = furst_instrument_paper.performance()
    assert (result.width > 0 * u.pix).all()
    assert (result.width < 1 * u.pix).all()


def test_resolving_power():
    """The instrument meets its resolving power requirement everywhere."""
    result = furst_instrument_paper.performance()
    assert (result.resolving_power > _performance.resolving_power_required).all()
