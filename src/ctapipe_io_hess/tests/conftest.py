#!/usr/bin/env python3

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def example_dst_path() -> Path:
    # TODO: return a real test file, from a server preferably
    return Path("/Users/kkosack/Data/HESS/DST/run_170720_DST_001_NonSplit.root")
