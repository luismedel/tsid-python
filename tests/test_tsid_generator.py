import threading

import pytest

from tsidpy import TSID, TSIDGenerator
import tsidpy.tsid as tsid_module


@pytest.mark.parametrize("kwargs, message", [
    ({"node": -1}, "Invalid node"),
    ({"node": 1, "node_bits": -1}, "Invalid node_bits"),
    ({"node": 1, "node_bits": 21}, "Invalid node_bits"),
    ({"node": 1, "node_bits": 0}, "too large"),
])
def test_generator_rejects_invalid_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        TSIDGenerator(**kwargs)


def test_generator_uses_explicit_node_and_counter_layout():
    generator = TSIDGenerator(node=255, node_bits=8, random_fn=lambda _: 0)

    tsid = generator.create()

    assert ((tsid.number & tsid_module.RANDOM_MASK) >> generator._counter_bits) == 255
    assert tsid.number & generator._counter_mask == 1


def test_generator_uses_custom_epoch(monkeypatch):
    fixed_seconds = 1700000000.0
    monkeypatch.setattr(tsid_module.time, "time", lambda: fixed_seconds)

    generator = TSIDGenerator(node=0, node_bits=0, epoch=0, random_fn=lambda _: 0)
    tsid = generator.create()

    assert tsid.timestamp == fixed_seconds * 1000


def test_generator_increments_counter_within_same_millisecond(monkeypatch):
    fixed_seconds = 1700000000.0
    monkeypatch.setattr(tsid_module.time, "time", lambda: fixed_seconds)

    generator = TSIDGenerator(node=1, node_bits=2, random_fn=lambda _: 0)
    first = generator.create()
    second = generator.create()

    assert first.number < second.number
    assert first.random == 1048577
    assert second.random == 1048578


def test_generator_advances_virtual_millisecond_on_counter_overflow(monkeypatch):
    fixed_seconds = 1700000000.0
    monkeypatch.setattr(tsid_module.time, "time", lambda: fixed_seconds)

    generator = TSIDGenerator(node=0, node_bits=20, random_fn=lambda _: 3)
    tsid = generator.create()

    assert tsid.timestamp == fixed_seconds * 1000 + 1
    assert tsid.random == 0


def test_set_default_generator_changes_tsid_create(monkeypatch):
    original = tsid_module._default_generator
    fixed_seconds = 1700000000.0
    monkeypatch.setattr(tsid_module.time, "time", lambda: fixed_seconds)

    generator = TSIDGenerator(node=3, node_bits=2, random_fn=lambda _: 0)
    TSID.set_default_generator(generator)

    try:
        created = TSID.create()
    finally:
        TSID.set_default_generator(original)

    assert created.random == 3145729


def test_tsid_create_is_unique_across_threads():
    original = tsid_module._default_generator
    generator = TSIDGenerator(node=0, node_bits=0, random_fn=lambda _: 0)
    created = []
    lock = threading.Lock()

    TSID.set_default_generator(generator)
    try:
        def worker():
            for _ in range(250):
                with lock:
                    created.append(TSID.create().number)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        TSID.set_default_generator(original)

    assert len(created) == 2000
    assert len(set(created)) == len(created)


def test_generator_is_unique_and_monotonic_across_threads():
    generator = TSIDGenerator(node=7, node_bits=4, random_fn=lambda _: 0)
    created = []
    lock = threading.Lock()

    def worker():
        for _ in range(250):
            number = generator.create().number
            with lock:
                created.append(number)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(created) == 2000
    assert len(set(created)) == len(created)
    assert created == sorted(created)
