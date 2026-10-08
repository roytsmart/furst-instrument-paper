import functools
import numpy as np
import named_arrays as na
import furst

__all__ = [
    "instrument",
]

axis_channel = "channel"
"""The logical axis along which the seven channels of FURST are arranged."""

axis_wavelength = "wavelength"
"""The logical axis of the wavelengths traced through each channel."""

axis_field = ("field_x", "field_y")
"""The logical axes of the positions sampled on the solar disk."""

axis_pupil = ("pupil_x", "pupil_y")
"""The logical axes of the positions sampled on the pupil."""

num_wavelength = 5
"""The number of wavelengths traced through each channel."""

num_field = 15
"""The number of samples along each axis of the solar disk."""

num_pupil = 15
"""The number of samples along each axis of the pupil."""

seed_field = 42
"""The seed of the random sample of the solar disk."""

seed_pupil = 43
"""The seed of the random sample of the pupil."""


@functools.cache
def instrument() -> furst.instruments.Instrument:
    """
    The FURST instrument as it was built and flown, sampled for the
    performance figures.

    This is :func:`furst.instruments.as_built`: the final design with the
    flight grating in place, the coatings and the filter as measured on the
    flight hardware, and the feed optic array moved to focus it.

    The solar disk and the pupil are each divided into a grid of cells, and
    one ray is traced through a point drawn uniformly at random inside each
    cell, so that the grid leaves no imprint on the line spread function.
    Each channel gets its own draw, so that the sampling noise is independent
    from channel to channel, and the draws are seeded so that every figure
    is reproducible.
    """
    result = furst.instruments.as_built(num_wavelength=num_wavelength)

    # the bounds of the sample carry the channel axis, so that each channel
    # is drawn separately instead of every channel sharing one draw
    ones = np.ones_like(na.value(result.feed_optic.rowland_azimuth))

    result.field = na.Cartesian2dVectorStratifiedRandomSpace(
        start=-ones,
        stop=+ones,
        axis=na.Cartesian2dVectorArray(*axis_field),
        num=num_field,
        centers=True,
        seed=seed_field,
    )
    result.pupil = na.Cartesian2dVectorStratifiedRandomSpace(
        start=-ones,
        stop=+ones,
        axis=na.Cartesian2dVectorArray(*axis_pupil),
        num=num_pupil,
        centers=True,
        seed=seed_pupil,
    )

    return result
