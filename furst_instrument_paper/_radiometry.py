import dataclasses
import functools
import numpy as np
import astropy.units as u
import named_arrays as na
import optika
import furst_instrument_paper
from ._instrument import axis_wavelength, axis_field, axis_pupil

__all__ = [
    "Radiometry",
    "radiometry",
]

num_wavelength = 21
"""The number of wavelengths sampled across each channel."""

num_field = 6
"""The number of points along each axis of the solar disk averaged over."""

num_pupil = 11
"""The number of points along each axis of the pupil traced from each point of the disk."""

seed = 0
"""The seed of the random positions drawn inside each cell of the pupil."""

unit_response = u.electron * u.cm**2 / u.erg
"""The unit of the response, which multiplies a line irradiance in erg per square centimeter per second."""


@dataclasses.dataclass(frozen=True)
class Radiometry:
    """
    The throughput of the instrument and the terms it is the product of.

    Every array is indexed by channel and by wavelength.
    """

    wavelength: na.AbstractScalar
    """The sampled wavelengths."""

    area_effective: na.AbstractScalar
    """
    The effective area, averaged over the solar disk.

    The area of the pupil traced from each point of the disk, weighted by
    the efficiency of every surface each ray meets, up to and including
    the absorption of the photon in the silicon of the sensor.
    """

    reflectance_feed: na.AbstractScalar
    """The reflectance of the coating of the feed optics."""

    efficiency_grating: na.AbstractScalar
    """
    The efficiency of the grating in the first order: the reflectance of its
    coating times the efficiency of its grooves, at the angle of incidence
    of each channel.
    """

    transmission_filter: na.AbstractScalar
    """The transmission of the visible-blind filter."""

    absorbance: na.AbstractScalar
    """The fraction of the light reaching the sensor which is absorbed in its silicon."""

    charge_collection: na.AbstractScalar
    """
    The fraction of the charge liberated by an absorbed photon which reaches
    a pixel.
    """

    quantum_yield: na.AbstractScalar
    """The number of electron-hole pairs liberated by each absorbed photon."""

    @property
    def efficiency(self) -> na.AbstractScalar:
        """The product of the efficiencies of every surface, up to the absorption in the sensor."""
        return (
            self.reflectance_feed
            * self.efficiency_grating
            * self.transmission_filter
            * self.absorbance
        )

    @property
    def area_collecting(self) -> na.AbstractScalar:
        """
        The area the instrument collects from: the effective area with the
        efficiency of every surface divided back out, which depends on the
        layout alone.
        """
        return self.area_effective / self.efficiency

    @property
    def quantum_efficiency(self) -> na.AbstractScalar:
        """
        The fraction of the photons reaching the sensor whose charge is
        collected, the product of its absorbance and its charge collection
        efficiency.
        """
        return self.absorbance * self.charge_collection

    @property
    def response(self) -> na.AbstractScalar:
        """
        The electrons the instrument records for a fluence of one unit of
        energy per unit area at its entrance.

        The effective area times the charge collection efficiency and the
        quantum yield of the sensor, divided by the energy of a photon.
        """
        energy = self.wavelength.to(u.erg, equivalencies=u.spectral()) / u.ph
        result = self.area_effective * self.charge_collection * self.quantum_yield
        return (result / energy).to(unit_response)


def _rays(
    wavelength: na.AbstractScalar,
    angle: u.Quantity | na.AbstractScalar = 0 * u.deg,
) -> optika.rays.RayVectorArray:
    """Rays of the given wavelengths meeting a surface at the given angle of incidence."""
    return optika.rays.RayVectorArray(
        wavelength=wavelength,
        position=na.Cartesian3dVectorArray() * u.mm,
        direction=na.Cartesian3dVectorArray(
            x=np.sin(angle),
            y=0,
            z=np.cos(angle),
        ),
    )


@functools.cache
def radiometry() -> Radiometry:
    """
    Compute the effective area of the instrument and the terms it is made
    of, following the design report of :mod:`furst`.

    The effective area comes from tracing a grid of rays across the pupil
    from each point of a grid on the solar disk. The terms are the
    efficiencies of the surfaces at the angles they are used at: near
    normal incidence for the feed optics, the filter, and the sensor, and
    at the angle of incidence of each channel for the grating.
    """
    instrument = furst_instrument_paper.instrument()
    instrument = dataclasses.replace(
        instrument,
        wavelength=na.linspace(
            start=instrument.wavelength.min(),
            stop=instrument.wavelength.max(),
            axis=axis_wavelength,
            num=num_wavelength,
        ),
    )
    system = instrument.system

    model = system.area_effective(
        field=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray(*axis_field),
            num=num_field,
        ),
        pupil=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray(*axis_pupil),
            num=num_pupil,
        ),
        seed=seed,
    )
    wavelength = model.wavelength.to(u.nm)

    normal = na.Cartesian3dVectorArray(0, 0, -1)
    rays = _rays(wavelength)
    rays_grating = _rays(wavelength, instrument.angle_grating_input)

    grating = instrument.grating
    efficiency_grating = grating.material.efficiency(rays_grating, normal)
    efficiency_grating = efficiency_grating * grating.rulings.efficiency(
        rays_grating, normal
    )

    sensor = system.sensor.material

    # the table behind the quantum yield has no pairs at the band gap of
    # silicon, 1.1 eV, and dividing by them there warns, harmlessly at the
    # energies of these photons
    with np.errstate(divide="ignore"):
        quantum_yield = sensor.quantum_yield_ideal(wavelength)

    return Radiometry(
        wavelength=wavelength,
        area_effective=model.area.to(u.mm**2),
        reflectance_feed=instrument.feed_optic.material.efficiency(rays, normal),
        efficiency_grating=efficiency_grating,
        transmission_filter=instrument.filter.material.efficiency(rays, normal),
        absorbance=sensor.efficiency(rays, normal),
        charge_collection=sensor.charge_collection_efficiency(wavelength=wavelength),
        quantum_yield=quantum_yield,
    )
