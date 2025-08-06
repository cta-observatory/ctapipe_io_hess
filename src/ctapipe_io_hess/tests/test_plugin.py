#!/usr/bin/env python3

from pathlib import Path

import numpy as np
from ctapipe.io import DataLevel, EventSource

from ctapipe_io_hess import HESSEventSource


def count_items(gen) -> int:
    """Count number of items in a generator, via brute force."""
    for ii, _ in enumerate(gen):
        pass
    return ii


def test_is_compatible(example_dst_path: Path, tmp_path: Path):
    """Check that we detect the file, and not a random ROOT file."""

    bad_root_file = tmp_path / "some_other_file.root"
    bad_root_file.write_text("Nothing in this file.")
    non_hess_file = tmp_path / "something_else.fits"

    assert HESSEventSource.is_compatible(example_dst_path)
    assert not HESSEventSource.is_compatible(bad_root_file)
    assert not HESSEventSource.is_compatible(non_hess_file)

    with EventSource(example_dst_path) as source:
        assert type(source) is HESSEventSource, "Didn't detect file type."


def test_length(example_dst_path: Path):
    with EventSource(example_dst_path) as source:
        assert len(source) == 10_000
        assert count_items(source) == 10_000

    with EventSource(example_dst_path, max_events=12) as source:
        assert len(source) == 12
        assert count_items(source) == 12


def test_read_hess_dst(example_dst_path: Path):
    """Test that the EventSoruce is set up correct and can read events."""

    with EventSource(example_dst_path) as source:
        assert type(source) is HESSEventSource, "Didn't detect file type."

        assert DataLevel.DL1_IMAGES in source.datalevels
        assert source.subarray.n_tels in [4, 5], "Expected 4 or 5 telescopes"
        assert source.is_simulation is False
        assert len(source.observation_blocks.keys()) >= 1, "Missing observation blocks"
        assert len(source.scheduling_blocks.keys()) >= 1, "Missing scheduling blocks"

        for event in source:
            assert len(event.dl1.tel) > 0, "Expected at least 1 telecope in the event"
            assert event.index.event_id > 0
            assert event.index.obs_id == 170720

            # check the images
            for tel_id, tel_event in event.dl1.tel.items():
                assert tel_event.image.shape == 960
                assert np.count_nonzero(tel_event.image) > 0
