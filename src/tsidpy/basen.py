
import typing as t

# Base 62
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(
    value: int,
    base: int,
    min_length: t.Optional[int] = None
) -> str:
    result: t.List[str] = []

    while True:
        result.append(ALPHABET[value % base])
        value //= base
        if value == 0:
            break

    if min_length and len(result) < min_length:
        result.extend(['0'] * (min_length - len(result)))

    return ''.join(result[::-1])


def decode(value: str, base: int) -> int:
    result: int = 0

    for c in value:
        result *= base
        result += ALPHABET.index(c)

    return result
