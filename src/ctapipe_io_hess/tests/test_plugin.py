#!/usr/bin/env python3

from collections import defaultdict
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


def test_generic_event_source(example_dst_path: Path):
    """Check that this meets the generic EventSource protocol."""

    with EventSource(example_dst_path) as source:
        assert type(source) is HESSEventSource, "Didn't detect file type."
        assert source.datalevels is not None, "Did not report datalevels"
        assert len(source.datalevels) > 0, "datalevels should not be empty"
        assert source.subarray.n_tels > 0, "Expected at least one telescope."
        assert len(source.observation_blocks.keys()) >= 1, "Missing observation blocks"
        assert len(source.scheduling_blocks.keys()) >= 1, "Missing scheduling blocks"

        seen_event_ids = defaultdict(int)

        for event in source:
            assert len(event.dl1.tel) > 0, "Expected at least 1 telecope in the event"
            assert event.index.event_id >= 0, "event_ids should be positive"
            assert event.index.obs_id >= 0, "obs_ids should be positive"
            seen_event_ids[(event.index.obs_id, event.index.event_id)] += 1

        # check uniqueness of event_ids within an obs_id
        for ids, count in seen_event_ids.items():
            assert count <= 1, f"(obs_ids={ids[0]}, event_id={ids[1]}) was not unique"


def test_read_hess_dst_specific(example_dst_path: Path):
    """Test that the EventSource is set up and the values are what are expected."""

    expected_obs_id = 170720

    with EventSource(example_dst_path, max_events=1000) as source:
        assert DataLevel.DL1_IMAGES in source.datalevels
        assert source.subarray.n_tels <= 5, "Expected up to 5 telescopes"
        assert source.is_simulation is False
        assert expected_obs_id in source.observation_blocks
        np.testing.assert_approx_equal(
            source.observation_blocks[expected_obs_id].actual_duration.to_value("min"),
            31.2,
        )
        assert source.observation_blocks[expected_obs_id].producer_id == "HESS"
        assert source.scheduling_blocks[expected_obs_id].producer_id == "HESS"

        # check the images
        for event in source:
            for tel_id, tel_event in event.dl1.tel.items():
                assert tel_id >= 0, "tel_id should be positive"
                assert tel_event.image is not None, "Image should exist"
                assert (
                    tel_event.image.shape[0] == 960
                ), "Image has unexpected number of pixels"
                assert (
                    np.count_nonzero(tel_event.image) > 0
                ), "Image should not be all 0s"


def test_process_to_dl2_geometry(example_dst_path, tmp_path):
    """
    Test full chain.

    Process a DST from DL1-images to generate DL1-parameteres and then
    DL2-geometry using ctapipe-process. If this works, then everything is fine!
    """
    pass  # TODO: implement me
