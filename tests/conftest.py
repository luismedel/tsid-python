import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_addoption(parser):
    parser.addoption(
        "--run-perf",
        action="store_true",
        default=False,
        help="run performance benchmarks marked with 'perf'",
    )
    parser.addoption(
        "--perf-loops",
        action="store",
        type=int,
        default=50000,
        help="iterations used by performance benchmarks",
    )
    parser.addoption(
        "--perf-repeats",
        action="store",
        type=int,
        default=5,
        help="number of repeated runs per performance scenario",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-perf"):
        return

    skip_perf = pytest.mark.skip(reason="use --run-perf to run performance tests")
    for item in items:
        if "perf" in item.keywords:
            item.add_marker(skip_perf)
