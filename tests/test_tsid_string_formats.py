import pytest

from tsidpy import TSID, TSID_CHARS
from tsidpy.tsid import TSID_HEXCHARS


@pytest.mark.parametrize("fmt, expected", [
    ("S", "0AWE5HZP3SKTK"),
    ("s", "0awe5hzp3sktk"),
    ("X", "0571C58FEC3CCF53"),
    ("x", "0571c58fec3ccf53"),
    ("d", "392311864492347219"),
    ("z", "Syn8NIURbX"),
])
def test_to_string_formats(fmt, expected):
    tsid = TSID.from_string("0AWE5HZP3SKTK")

    assert tsid.to_string(fmt) == expected


@pytest.mark.parametrize("fmt, value", [
    ("S", "0AXFXR5W7VBX0"),
    ("s", "0axfxr5w7vbx0"),
    ("X", "0575FDC1787DAFA0"),
    ("x", "0575fdc1787dafa0"),
    ("d", "393499549856804768"),
    ("z", "T4EOF2kj0S"),
])
def test_from_string_round_trip_across_formats(fmt, value):
    tsid = TSID.from_string(value, fmt)

    assert tsid.to_string(fmt) == value
    assert TSID.from_string(tsid.to_string(fmt), fmt) == tsid


def test_crockford_parsing_accepts_ambiguous_characters():
    canonical = TSID.from_string("0000000000001")

    assert TSID.from_string("000000000000l") == canonical
    assert TSID.from_string("000000000000i") == canonical
    assert TSID.from_string("000000000000o") == TSID(0)


def test_from_string_rejects_invalid_canonical_length():
    with pytest.raises(ValueError, match=str(TSID_CHARS)):
        TSID.from_string("short")


@pytest.mark.parametrize("fmt", ["X", "x"])
def test_from_string_rejects_invalid_hex_length(fmt):
    with pytest.raises(ValueError, match=str(TSID_HEXCHARS)):
        TSID.from_string("abcd", fmt)


def test_to_string_rejects_invalid_format():
    with pytest.raises(ValueError, match="Invalid format"):
        TSID(1).to_string("q")


def test_from_string_rejects_invalid_format():
    with pytest.raises(ValueError, match="Invalid format"):
        TSID.from_string("0AWE5HZP3SKTK", "q")
