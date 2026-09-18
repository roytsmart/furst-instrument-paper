import dataclasses
import functools
import numpy as np
import astropy.units as u
import named_arrays as na
import furst_instrument_paper
from ._instrument import axis_wavelength, axis_field, axis_pupil

__all__ = [
    "Performance",
    "performance",
]

resolving_power_required = 20000
"""The resolving power FURST is required to achieve."""


@dataclasses.dataclass(frozen=True)
class Performance:
    """
    The spectral performance of the instrument at the traced wavelengths.

    Every array is indexed by channel and by wavelength.
    """

    wavelength: na.AbstractScalar
    """The traced wavelengths."""

    width: na.AbstractScalar
    """
    The width of the disk-integrated line spread function, in pixels.

    The standard deviation of the positions of the rays along the dispersion
    direction, over the whole solar disk and the whole pupil, added in
    quadrature with the standard deviation of a uniform distribution one
    pixel wide, which accounts for the finite size of the pixels.
    """

    dispersion: na.AbstractScalar
    """The change in wavelength per unit distance along the detector."""

    resolving_power: na.AbstractScalar
    """
    The ratio of the wavelength to the smallest resolvable wavelength
    difference, which is taken to be twice the width of the line spread
    function.
    """


@functools.cache
def performance() -> Performance:
    """
    Trace the instrument and measure its spectral performance.

    This follows the original design study: the rays which reach the
    detector are gathered for each wavelength of each channel, the width of
    their distribution along the dispersion direction is the width of the
    line spread function, and the dispersion of each channel is read from
    the positions of its outermost wavelengths.
    """
    instrument = furst_instrument_paper.instrument()
    system = instrument.system

    rays = system.rayfunction_default.outputs

    weight = rays.unvignetted.astype(float)
    axes_disk = axis_field + axis_pupil

    width_pixel = system.sensor.width_pixel

    position = rays.position
    position_mean = (position * weight).sum(axes_disk) / weight.sum(axes_disk)

    dx = (position.x - position_mean.x) / width_pixel
    dx = dx.to(u.dimensionless_unscaled) * u.pix

    variance_geometric = (np.square(dx) * weight).sum(axes_disk)
    variance_geometric = variance_geometric / weight.sum(axes_disk)
    variance_pixel = np.square(1 * u.pix) / 12
    width = np.sqrt(variance_geometric + variance_pixel)

    wavelength = instrument.wavelength_physical.to(u.nm)

    index_first = {axis_wavelength: 0}
    index_last = {axis_wavelength: ~0}
    dispersion = wavelength[index_last] - wavelength[index_first]
    dispersion = dispersion / (position_mean.x[index_last] - position_mean.x[index_first])
    dispersion = dispersion.to(u.nm / u.mm)

    wavelength_resolvable = 2 * width * (width_pixel / u.pix) * dispersion
    resolving_power = wavelength / wavelength_resolvable
    resolving_power = resolving_power.to(u.dimensionless_unscaled)

    return Performance(
        wavelength=wavelength,
        width=width,
        dispersion=dispersion,
        resolving_power=resolving_power,
    )
