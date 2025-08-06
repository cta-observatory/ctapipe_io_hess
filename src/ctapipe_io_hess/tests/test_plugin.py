#!/usr/bin/env python3

from pathlib import Path
from ctapipe.io import EventSource, DataLevel

def test_read_hess_dst(example_dst_path: Path):
    """Test that the EventSoruce is set up correct and can read events."""

    with EventSource(example_dst_path) as source:

        assert DataLevel.DL1_IMAGES in source.datalevels
        assert source.subarray.n_tels in [4,5], "Expected 4 or 5 telescopes"
        assert source.is_simulation is False
        assert len(source.observation_blocks.keys())>=1, "Missing observation blocks"
        assert len(source.scheduling_blocks.keys())>=1, "Missing scheduling blocks"

        for event in source:
            for tel_id, tel_event in event.dl1.items():
                assert tel_event.image.shape == 960
