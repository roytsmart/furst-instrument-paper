import astropy.units as u
import named_arrays as na
import furst_instrument_paper
from furst_instrument_paper import _instrument, _radiometry


def test_radiometry():
    result = furst_instrument_paper.radiometry()
    assert isinstance(result, furst_instrument_paper.Radiometry)

    shape = {
        _instrument.axis_channel: 7,
        _instrument.axis_wavelength: _radiometry.num_wavelength,
    }
    assert result.wavelength.shape == shape
    assert result.area_effective.shape == shape
    assert result.response.shape == shape

    assert na.unit(result.wavelength).is_equivalent(u.nm)
    assert na.unit(result.area_effective).is_equivalent(u.mm**2)
    assert na.unit(result.response).is_equivalent(_radiometry.unit_response)


def test_efficiencies():
    """Every term of the effective area is a fraction of the light."""
    result = furst_instrument_paper.radiometry()
    terms = [
        result.reflectance_feed,
        result.efficiency_grating,
        result.transmission_filter,
        result.absorbance,
        result.charge_collection,
    ]
    for term in terms:
        assert (term > 0).all()
        assert (term < 1).all()


def test_area_collecting():
    """
    With the efficiencies divided back out, every channel collects from the
    same few square millimeters, which is a check on the whole chain.
    """
    area = furst_instrument_paper.radiometry().area_collecting
    assert (area > 2.5 * u.mm**2).all()
    assert (area < 4 * u.mm**2).all()


def test_response():
    """
    The quantum yield of silicon grows almost with the energy of a photon,
    so per unit energy the detector is nearly flat, and the response follows
    the effective area to within a few tens of percent.
    """
    result = furst_instrument_paper.radiometry()
    assert (result.quantum_yield > 1 * u.electron / u.ph).all()

    # counted in electrons, not corrected for the quantum yield, so it is
    # larger than the fraction of the photons whose charge is collected
    quantum_efficiency = result.quantum_efficiency
    assert na.unit(quantum_efficiency).is_equivalent(u.electron / u.ph)
    fraction = result.absorbance * result.charge_collection * (u.electron / u.ph)
    assert (quantum_efficiency > fraction).all()

    ratio = result.response / result.area_effective
    ratio = ratio / ratio.max()
    assert (ratio > 0.7).all()
