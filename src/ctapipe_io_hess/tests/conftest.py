#!/usr/bin/env python3

from pathlib import Path

import pytest
from ctapipe.utils import get_dataset_path


@pytest.fixture(scope="session")
def example_dst_path() -> Path:
    """Returns an example HESS DST file written with no tree splitting for the Intensity data."""
    return get_dataset_path("example_hess_dst.root")
