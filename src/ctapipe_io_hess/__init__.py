"""Plugin for ctapipe for reading HESS DST data."""

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import astropy.units as u
import numpy as np
import uproot
from astropy.coordinates import EarthLocation
from astropy.utils import lazyproperty
from ctapipe.containers import (
    DL1CameraContainer,
    DL1Container,
    EventIndexContainer,
    EventType,
    ObservationBlockContainer,
    ObservingMode,
    PointingContainer,
    PointingMode,
    SchedulingBlockContainer,
    SchedulingBlockType,
    TelescopePointingContainer,
    TriggerContainer,
)
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

from .version import __version__

__all__ = [
    "__version__",
    "HESSEventSource",
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
DUMMY_SUBARRAY = SubarrayDescription(
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


def _extract_run_header(run_tree):
    """Get all readable elements of the RunHeader.

    A bit of a hack to avoid reading items without streamers:
    """
    metadata = dict()
    run_header = run_tree["RunHeader"]
    for k, v in filter(lambda x: x[0][0] == "f", run_header.items()):
        value = None
        try:
            value = v.array()[
                -1
            ]  # take the last element, in case there is more than one run header
        except Exception:
            value = f"CANNOT READ TYPE: {v.typename}"

        metadata[k[1:]] = value  # strips off the leading "f"

    return metadata


@dataclass
class DSTMetadata:
    """Describes aspects of the file."""

    num_subarray_events: int
    run_header: dict


class HESSEventSource(EventSource):
    """EventSource for HESS DSTs."""

    # EventSource properties that must be overridden here or as functions:
    is_simulation = False
    simulation_config = False

    # ==========================================================================
    # Internal methods
    # ==========================================================================

    @lazyproperty
    def _metadata(self) -> DSTMetadata:
        """Return dictionary of metadata from the DST file."""
        with uproot.open(self.input_url) as root_file:
            dst_tree = root_file["DST_tree"]
            n_events = dst_tree.num_entries
            run_tree = root_file["run_tree"]
            run_header = _extract_run_header(run_tree)

        return DSTMetadata(
            num_subarray_events=n_events,
            run_header=run_header,
        )

    # ==========================================================================
    # Methods of EventSource the must be implemented
    # ==========================================================================

    @property
    def subarray(self) -> SubarrayDescription:
        """Return Subarray."""
        return DUMMY_SUBARRAY

    @classmethod
    def is_compatible(cls, file_path: Path) -> bool:
        """Check that path is a HESS DST."""
        # must be a ROOT file
        if not str(file_path).endswith(".root"):
            return False

        # if it's a ROOT file, let's check inside that it is a HESS DST:
        try:
            with uproot.open(file_path) as potential_dst:
                if "DST_tree" in potential_dst:
                    return True
                return False
        except OSError:
            # just in case it's not even a real ROOT file
            return False

    @property
    def observation_blocks(self) -> dict[int, ObservationBlockContainer]:
        """
        Return dict of OBs.

        For HESS DSTs this always just one, with the obs_id being the run
        number.
        """
        run_header = self._metadata.run_header
        obs_id = run_header["RunNum"]

        return {
            obs_id: ObservationBlockContainer(
                obs_id=obs_id,
                sb_id=obs_id,  # none for HESS, what to put here?
                producer_id="HESS",
                actual_duration=run_header["Duration"] * u.s,
            )
        }

    @property
    def scheduling_blocks(self) -> dict[int, SchedulingBlockContainer]:
        """Return the dict of SBs.

        For HESS, there is no notion of Scheduling Block, so we can just maybe reuse the run id?
        """
        run_header = self._metadata.run_header
        sb_id = run_header["RunNum"]
        sb_type = SchedulingBlockType.CALIBRATION
        if "observation" in run_header["RunType"].lower():
            sb_type = SchedulingBlockType.OBSERVATION

        # TODO: how to determine these?
        obs_mode = ObservingMode.WOBBLE
        pnt_mode = PointingMode.TRACK

        return {
            sb_id: SchedulingBlockContainer(
                sb_id=sb_id,
                producer_id="HESS",
                sb_type=sb_type,
                observing_mode=obs_mode,
                pointing_mode=pnt_mode,
            )
        }

    @property
    def datalevels(self) -> tuple[DataLevel]:
        """Return datalevels tuple."""
        return (DataLevel.DL1_IMAGES,)

    def _generator(self) -> Generator[ArrayEventContainer, None, None]:
        # open the file and loop over events, extracting the images and
        # image_masks (which are the cleaning masks where 1="good"

        with uproot.open(self.input_url) as dst_file:
            dst_tree = dst_file["DST_tree"]
            branches_to_load = [
                "EventHeader/fGlobalEvtNum",
                "EventHeader/fGlobalBunchNum",
            ]
            obs_id = self._metadata.run_header["RunNum"]

            # CODE TO LOOP OVER EVENTS HERE
            for count, entries in enumerate(
                dst_tree.iterate(
                    branches_to_load, step_size=1, entry_stop=self.max_events
                )
            ):
                entry = entries[0]  # since entries is an array length step_size
                bunch_num = entry["EventHeader/fGlobalBunchNum"]
                event_num = entry["EventHeader/fGlobalEvtNum"]

                event_id = (np.int64(bunch_num) << 32) + event_num
                tels_with_data = [1, 2, 3, 4]  # TODO: read this!
                tels_with_trigger = [1, 2, 3, 4, 5]  # TODO read this

                # Loop over telescopes in the event, and fill the DL1 info for
                # each Telescope Event
                tel_camera = {}
                tel_pointing = {}

                for tel_id in tels_with_data:
                    image = np.zeros(960, dtype=np.float32)  # TODO: load it
                    image_mask = np.zeros(960, dtype=np.float32)  # TODO: load it

                    tel_camera[tel_id] = DL1CameraContainer(
                        image=image, image_mask=image_mask
                    )

                    tel_pointing[tel_id] = TelescopePointingContainer(
                        azimuth=0 * u.deg, altitude=0 * u.deg
                    )

                # Now yield the array event
                yield ArrayEventContainer(
                    index=EventIndexContainer(event_id=event_id, obs_id=obs_id),
                    count=count,
                    trigger=TriggerContainer(
                        tels_with_trigger=tels_with_trigger,
                        event_type=EventType.SUBARRAY,  # HESS has no interleved events?
                    ),
                    dl1=DL1Container(tel=tel_camera),
                    pointing=PointingContainer(tel=tel_pointing),
                )

    # ==========================================================================
    # Other protocol methods
    # ==========================================================================

    def __len__(self) -> int:
        """Support using len(source) to get the number of events.

        This also makes the progress bar work when using this event source.
        """
        if self.max_events:
            return max(self.max_events, self._metadata.num_subarray_events)
        return self._metadata.num_subarray_events
