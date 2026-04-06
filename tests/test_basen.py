from tsidpy.basen import decode, encode


def test_encode_and_decode_base_10():
    value = 437283649808777971

    encoded = encode(value, 10)

    assert encoded == "437283649808777971"
    assert decode(encoded, 10) == value


def test_encode_and_decode_base_16():
    value = 0x575FDC1787DAFA0

    encoded = encode(value, 16, min_length=16)

    assert encoded == "0575FDC1787DAFA0"
    assert decode(encoded, 16) == value


def test_encode_and_decode_base_62():
    value = 437283649808777971

    encoded = encode(value, 62)

    assert encoded == "WIlLsHwljH"
    assert decode(encoded, 62) == value


def test_encode_zero_with_padding():
    assert encode(0, 16, min_length=4) == "0000"


def test_decode_single_digit_values():
    assert decode("0", 10) == 0
    assert decode("F", 16) == 15
    assert decode("z", 62) == 61
