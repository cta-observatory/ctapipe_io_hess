"""Plugin for ctapipe for reading HESS DST data."""

from .version import __version__
import astropy.units as u
import numpy as np
from astropy.coordinates import EarthLocation

from ctapipe.containers import (
    DL1Container,
    ObservationBlockContainer,
    ReconstructedGeometryContainer,
    SchedulingBlockContainer,
)
from ctapipe.core import traits
from ctapipe.instrument import (
    CameraDescription,
    CameraGeometry,
    CameraReadout,
    OpticsDescription,
    ReflectorShape,
    SizeType,
    SubarrayDescription,
    TelescopeDescription,
)
from ctapipe.io import DataLevel, EventSource
from ctapipe.io.datawriter import ArrayEventContainer
from ctapipe.reco import Reconstructor

__all__ = [
    "__version__",
    "PluginEventSource",
    "PluginReconstructor",
]

# TODO: replace this with one built from real data in the DST
optics = OpticsDescription(
    "HESS1",
    size_type=SizeType.MST,
    n_mirrors=1,
    equivalent_focal_length=28 * u.m,
    effective_focal_length=29 * u.m,
    mirror_area=400 * u.m**2,
    n_mirror_tiles=250,
    reflector_shape=ReflectorShape.PARABOLIC,
)

step = 0.1
t = np.arange(0, 40, step)
geometry = CameraGeometry.make_rectangular()
camera = CameraDescription(
    name="1U",
    geometry=geometry,
    readout=CameraReadout(
        name="plugin",
        sampling_rate=1 * u.GHz,
        reference_pulse_shape=np.exp(-0.5 * (t - 10) ** 2 / 4),
        reference_pulse_sample_width=step * u.ns,
        n_channels=2,
        n_pixels=geometry.n_pixels,
        n_samples=40,
    ),
)


telescopes = [
    TelescopeDescription(f"CT{i+1}", optics=optics, camera=camera) for i in range(4)
]

# TODO: do this right, these are not correct, just an example.
subarray = SubarrayDescription(
    name="HESS",
    tel_descriptions={
        1: telescopes[0],
        2: telescopes[1],
        3: telescopes[2],
        4: telescopes[3],
    },
    tel_positions={
        1: [-40, 0, 0] * u.m,
        2: [40, 0, 0] * u.m,
        3: [0, 40, 0] * u.m,
        4: [0, -40, 0] * u.m,
    },
    reference_location=EarthLocation(
        lat=-23.2771843 * u.deg, lon=16.5051989 * u.deg, height=1800 * u.m
    ),
)


class HESSEventSource(EventSource):
    """EventSource for HESS DSTs."""

    is_simulation = False
    datalevels = (DataLevel.DL1_IMAGES,)
    subarray = subarray
    observation_blocks = {1: ObservationBlockContainer(obs_id=1)}
    scheduling_blocks = {1: SchedulingBlockContainer(sb_id=1)}

    @classmethod
    def is_compatible(cls, path):
        # TODO: replace with a real check that this is a HESS DST (have to open it with uproot)
        return str(path).endswith(".root")

    def _generator(self):
        for i in range(10):
            yield ArrayEventContainer(
                count=i,
                dl1=DL1Container(

                )
            )
