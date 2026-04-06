from datetime import datetime

import pytest

from tsidpy import TSID, TSID_EPOCH
from tsidpy.tsid import RANDOM_BITS


def test_number_is_wrapped_to_64_bits():
    assert TSID(0x10000000000000000).number == 0


def test_timestamp_and_datetime_are_derived_from_number():
    tsid = TSID(1 << RANDOM_BITS)

    assert tsid.timestamp == TSID_EPOCH + 1
    assert tsid.datetime == datetime.fromtimestamp((TSID_EPOCH + 1) / 1000)


def test_random_component_extracts_low_bits():
    assert TSID((0xFFFFFFFF << RANDOM_BITS) + 255).random == 255


def test_string_representation_is_canonical():
    tsid = TSID(0x000000000000000A)

    assert str(tsid) == "000000000000A"
    assert repr(tsid) == "000000000000A"


def test_hash_and_equality_behave_like_underlying_integer():
    first = TSID(0xFFCAFEFABADABEEF)
    same = TSID(0xFFCAFEFABADABEEF)
    other = TSID(1)

    assert first == same
    assert first != other
    assert first != 0
    assert hash(first) == hash(first.number)


def test_ordering_uses_numeric_value():
    lower = TSID(0)
    higher = TSID(1)

    assert lower < higher
    assert higher > lower
    assert not (lower < 1000)


def test_to_bytes_round_trip():
    tsid = TSID(0xFFCAFEFABADABEEF)

    raw = tsid.to_bytes()

    assert raw == b"\xff\xca\xfe\xfa\xba\xda\xbe\xef"
    assert TSID.from_bytes(raw) == tsid


def test_from_bytes_rejects_invalid_length():
    with pytest.raises(ValueError, match="Invalid TSID bytes"):
        TSID.from_bytes(b"\x00")
