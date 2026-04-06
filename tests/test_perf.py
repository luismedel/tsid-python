import platform
import statistics
import sys
import threading
import time
from datetime import datetime
from uuid import uuid4

import pytest

from tsidpy import TSID, TSIDGenerator


THREAD_COUNTS = (1, 2, 4, 8)


def _measure(factory, loops):
    started = time.perf_counter()
    for _ in range(loops):
        factory()
    elapsed = time.perf_counter() - started
    rate = loops / elapsed if elapsed else float("inf")
    return elapsed, rate


def _repeat_measure(factory, loops, repeats):
    runs = []
    for _ in range(repeats):
        elapsed, rate = _measure(factory, loops)
        runs.append({"elapsed": elapsed, "rate": rate})
    return runs


def _summarize_runs(runs):
    rates = [run["rate"] for run in runs]
    min_rate = min(rates)
    max_rate = max(rates)
    mean_rate = statistics.mean(rates)
    spread_pct = ((max_rate - min_rate) / mean_rate * 100) if mean_rate else 0.0
    return {
        "min_rate": min_rate,
        "mean_rate": mean_rate,
        "max_rate": max_rate,
        "spread_pct": spread_pct,
    }


def _measure_shared_generator(threads, loops):
    generator = TSIDGenerator(node=1)
    created = []

    def worker():
        for _ in range(loops):
            generator.create().number

    started = time.perf_counter()
    for _ in range(threads):
        thread = threading.Thread(target=worker)
        created.append(thread)
        thread.start()
    for thread in created:
        thread.join()
    elapsed = time.perf_counter() - started
    total_ops = threads * loops
    total_rate = total_ops / elapsed if elapsed else float("inf")
    per_thread_rate = total_rate / threads
    return {
        "threads": threads,
        "elapsed": elapsed,
        "total_rate": total_rate,
        "per_thread_rate": per_thread_rate,
    }


def _print_header(loops, repeats):
    print("== tsidpy performance report ==")
    print("generated_at: {}".format(datetime.utcnow().isoformat() + "Z"))
    print("python: {}".format(sys.version.split()[0]))
    print("platform: {}".format(platform.platform()))
    print("loops: {}".format(loops))
    print("repeats: {}".format(repeats))
    print("")


def _print_single_thread_section(title, scenarios, loops, repeats):
    print("== {} ==".format(title))
    print(
        "{:<24} {:>9} {:>12} {:>12} {:>12} {:>10}".format(
            "scenario",
            "loops",
            "ops/s min",
            "ops/s mean",
            "ops/s max",
            "spread %",
        )
    )
    for label, factory in scenarios:
        summary = _summarize_runs(_repeat_measure(factory, loops, repeats))
        print(
            "{:<24} {:>9} {:>12.0f} {:>12.0f} {:>12.0f} {:>9.2f}".format(
                label,
                loops,
                summary["min_rate"],
                summary["mean_rate"],
                summary["max_rate"],
                summary["spread_pct"],
            )
        )
    print("")


def _print_contention_section(loops):
    print("== contention_shared_generator ==")
    print(
        "{:<8} {:>9} {:>14} {:>14} {:>12}".format(
            "threads",
            "loops",
            "ops/s total",
            "ops/s thread",
            "speedup",
        )
    )
    baseline = None
    for threads in THREAD_COUNTS:
        result = _measure_shared_generator(threads, loops)
        if baseline is None:
            baseline = result["total_rate"]
        speedup = result["total_rate"] / baseline if baseline else 0.0
        print(
            "{:<8} {:>9} {:>14.0f} {:>14.0f} {:>12.2f}".format(
                result["threads"],
                loops,
                result["total_rate"],
                result["per_thread_rate"],
                speedup,
            )
        )
    print("")


@pytest.mark.perf
def test_generation_benchmarks_are_reported(request):
    loops = request.config.getoption("--perf-loops")
    repeats = request.config.getoption("--perf-repeats")
    canonical = "0AWE5HZP3SKTK"
    hex_value = "0571C58FEC3CCF53"
    tsid = TSID.from_string(canonical)
    raw = tsid.to_bytes()
    explicit_generator = TSIDGenerator(node=1)

    _print_header(loops, repeats)
    _print_single_thread_section(
        "generation",
        [
            ("tsid_default_number", lambda: TSID.create().number),
            ("tsid_generator_number", lambda: explicit_generator.create().number),
            ("tsid_default_string", lambda: str(TSID.create())),
        ],
        loops,
        repeats,
    )
    _print_single_thread_section(
        "serialization",
        [
            ("tsid_to_string_S", lambda: str(tsid)),
            ("tsid_to_string_X", lambda: tsid.to_string("X")),
            ("tsid_to_bytes", tsid.to_bytes),
        ],
        loops,
        repeats,
    )
    _print_single_thread_section(
        "deserialization",
        [
            ("tsid_from_string_S", lambda: TSID.from_string(canonical)),
            ("tsid_from_string_X", lambda: TSID.from_string(hex_value, "X")),
            ("tsid_from_bytes", lambda: TSID.from_bytes(raw)),
        ],
        loops,
        repeats,
    )
    _print_single_thread_section(
        "external_reference",
        [
            ("uuid4", uuid4),
            ("uuid4_string", lambda: str(uuid4())),
        ],
        loops,
        repeats,
    )
    _print_contention_section(loops)

    assert repeats > 0
