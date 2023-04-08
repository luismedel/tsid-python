
import functools
import threading

import typing as t

from datetime import datetime, timedelta
from random import random

from .basen import decode, encode

TSID_BYTES: int = 8
TSID_CHARS: int = 13

TSID_EPOCH: datetime = datetime.fromisoformat("2020-01-01")
_TSID_EPOCH_MILLIS = int(TSID_EPOCH.timestamp() * 1000)

RANDOM_BITS: int = 22
RANDOM_MASK: int = 0x3fffff

NODE_ID: int = int(random() * 0xffffffff)

ALPHABET: str = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
ALPHABET_VALUES: list[int] = [-1 for _ in range(128)]


def __set_alphabet_values(chars: str, start: int) -> None:
    for i, c in enumerate(chars):
        ALPHABET_VALUES[ord(c)] = start + i
        ALPHABET_VALUES[ord(c.upper())] = start + i


__set_alphabet_values('0123456789', 0)
__set_alphabet_values('abcdefghjkmnpqrstvwxyz', 0xa)
__set_alphabet_values('oi', 0)
__set_alphabet_values('l', 1)


_default_generator: 'TSIDGenerator'


@functools.total_ordering
class TSID:
    """A value object that represents a Time-Sorted Unique Identifier (TSID).

       TSID is a 64-bit value that has 2 components:

       - Time component (42 bits): a number of milliseconds since 2020-01-01
         (Unix epoch).
       - Random component (22 bits): a sequence of random bits generated by a
         secure random generator.

       The Random component has 2 sub-parts:
       - Node (0 to 20 bits): a number used to identify the machine or node.
       - Counter (2 to 22 bits): a randomly generated number that is
         incremented whenever the time component is repeated.

       The random component layout depend on the node bits. If the node bits
       are 10, the counter bits are limited to 12. In this example, the
       maximum node value is `2^10-1 = 1023` and the maximum counter value is
       `2^12-1 = 4093`. So the maximum TSIDs that can be generated per
       millisecond per node is `4096`.

       Instances of this class are immutable.

       See [Snowflake ID](https://en.wikipedia.org/wiki/Snowflake_ID).
    """

    def __init__(self, number: int) -> None:
        """
        >>> TSID(0x10000000000000000).number == 0
        True
        """
        self.__number: int = number & 0xffffffffffffffff  # 64-bit

    @property
    def datetime(self, epoch: datetime | None = None) -> datetime:
        """Returns the time component of the TSID.

        >>> TSID(0).datetime == TSID_EPOCH
        True
        >>> delta = timedelta(milliseconds=1)
        >>> TSID(1 << RANDOM_BITS).datetime == TSID_EPOCH + delta
        True
        """
        epoch = epoch or TSID_EPOCH
        return epoch + timedelta(milliseconds=self.__number >> RANDOM_BITS)

    @property
    def random(self) -> int:
        """Returns the random component of the TSID.

        >>> TSID(0).random == 0
        True
        >>> TSID(1).random == 1
        True
        >>> TSID((0xffffffff << RANDOM_BITS) + 255).random == 255
        True
        """
        return self.__number & RANDOM_MASK

    @property
    def number(self) -> int:
        """Converts the TSID into a 64-bit number.

           This simply unwraps the internal value

        >>> TSID(0xffff0000000000000000).number == 0
        True
        >>> TSID(0x0000000000000000).number == 0
        True
        >>> TSID(0xffff).number == 0xffff
        True
        """
        return self.__number

    def __lt__(self, __value: object) -> bool:
        """
        >>> TSID(0) < TSID(1)
        True
        >>> TSID(0) < 1000
        False
        """
        if isinstance(__value, TSID):
            return self.__number < __value.__number
        return False

    def __eq__(self, __value: object) -> bool:
        """
        >>> TSID(0) == TSID(0)
        True
        >>> TSID(0) != 0
        True
        >>> TSID(0) != '0'
        True
        """
        if isinstance(__value, TSID):
            return self.__number == __value.__number
        return False

    def __repr__(self) -> str:
        return self._to_canonical_string()

    def __str__(self) -> str:
        return self._to_canonical_string()

    def to_bytes(self) -> bytes:
        r"""Converts the TSID into a byte array.

        >>> t = TSID(1)
        >>> t.to_bytes() == b'\x00\x00\x00\x00\x00\x00\x00\x01'
        True
        >>> t = TSID(0xfabada)
        >>> t.to_bytes() == b'\x00\x00\x00\x00\x00\xfa\xba\xda'
        True
        >>> t = TSID(0xffcafefabadabeef)
        >>> t.to_bytes() == b'\xff\xca\xfe\xfa\xba\xda\xbe\xef'
        True
        >>> t = TSID(0xffffffcafefabadabeef)
        >>> t .to_bytes() == b'\xff\xca\xfe\xfa\xba\xda\xbe\xef'
        True
        """
        return self.__number.to_bytes(TSID_BYTES, byteorder='big',
                                      signed=False)

    def to_string(self, format: str | None = None) -> str:
        """Converts the TSID into a string.

           Supports the following formats:
            - `S`: canonical string in upper case.
            - `s`: canonical string in lower case.
            - `X`: hexadecimal in upper case.
            - `x`: hexadecimal in lower case.
            - `d`: base-10.
            - `z`: base-62.

        >>> t = TSID.from_string('0AWE5HZP3SKTK')
        >>> t.to_string('S')
        '0AWE5HZP3SKTK'
        >>> t.to_string('x')
        '0571c58fec3ccf53'
        >>> t = TSID.from_string('0AXFXR5W7VBX0')
        >>> t.to_string('X')
        '0575FDC1787DAFA0'
        >>> t = TSID(0xffffffffffffffff)
        >>> t.to_string()
        'FZZZZZZZZZZZZ'
        >>> t = TSID(0x000000000000000a)
        >>> t.to_string()
        '000000000000A'
        """

        if format is None:
            return str(self)

        match format:
            case 'S':  # canonical string in upper case
                return self._to_canonical_string()
            case 's':  # canonical string in lower case
                return self._to_canonical_string().lower()
            case 'X':  # hexadecimal in upper case
                return encode(self.number, 16, min_length=TSID_BYTES*2)
            case 'x':  # hexadecimal in lower case
                return encode(self.number, 16, min_length=TSID_BYTES*2).lower()
            case 'd':  # base-10
                return encode(self.number, 10)
            case 'z':  # base-62
                return encode(self.number, 62)
            case _:
                raise ValueError(f"Invalid format: '{format}'")

    def _to_canonical_string(self) -> str:
        return ''.join(ALPHABET[self.__number >> i & 0x1f]
                       for i in range(60, -5, -5))

    @staticmethod
    def create() -> 'TSID':
        """Returns a new TSID.

           This static method is a quick alternative to
           `TSIDGenerator::create()`.

           It can generate up to `2^22` (`4,194,304`) TSIDs per millisecond.
           It can be useful, for example, for logging.

           Security-sensitive applications that require a cryptographically
           secure pseudo-random generator should use `TSIDGenerator::create()`.

           > Note this method is not thread safe by default. It's the
           TSIDGenerator responsibility to ensure thread safety.

        >>> a = TSID.create()
        >>> b = TSID.create()
        >>> c = TSID.create()
        >>> a.number < b.number < c.number
        True
        >>> a.datetime == b.datetime == c.datetime
        True
        >>> a.random < b.random < c.random
        True
        """
        return _default_generator.create()

    @staticmethod
    def from_bytes(bytes: bytes) -> 'TSID':
        r"""Converts a byte array into a TSID.

        >>> TSID.from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x00') == TSID(0)
        True
        >>> TSID.from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x01') == TSID(1)
        True
        >>> TSID.from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x02') == TSID(2)
        True
        >>> TSID.from_bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0b') == TSID(11)
        True
        """
        if len(bytes) != TSID_BYTES:
            raise ValueError(f'Invalid TSID bytes (len {len(bytes)}, '
                             f'expected {TSID_BYTES})')

        number: int = int.from_bytes(bytes, byteorder='big', signed=False)
        return TSID(number)

    @staticmethod
    def from_string(string: str, format: str | None = None) -> 'TSID':
        """Converts a string into a TSID.

           Supports the following formats:
            - `S`: canonical string in upper case.
            - `s`: canonical string in lower case.
            - `X`: hexadecimal in upper case.
            - `x`: hexadecimal in lower case.
            - `d`: base-10.
            - `z`: base-62.

        >>> t1 = TSID.from_string('0575FDC1787DAFA0', 'X')
        >>> t2 = TSID.from_string('0AXFXR5W7VBX0')
        >>> t1.number == t2.number
        True
        """
        number: int

        if format is None or format in ('S', 's'):
            if len(string) != TSID_CHARS:
                raise ValueError("Invalid TSID string")

            number = sum(ALPHABET_VALUES[ord(string[i])] << h
                         for i, h in enumerate(range(60, -5, -5), 0))
        else:
            match format:
                case 'X':  # hexadecimal in upper case
                    number = decode(string, 16)
                case 'x':  # hexadecimal in lower case
                    number = decode(string.upper(), 16,)
                case 'd':  # base-10
                    number = decode(string, 10)
                case 'z':  # base-62
                    number = decode(string, 62)
                case _:
                    raise ValueError(f"Invalid format: '{format}'")
        return TSID(number)

    @staticmethod
    def set_default_generator(generator: 'TSIDGenerator') -> None:
        """Sets the default TSID generator.

        >>> generator: TSIDGenerator = TSIDGenerator(node=1)
        >>> TSID.set_default_generator(generator)
        """
        global _default_generator
        _default_generator = generator


def _rnd_generator() -> int:
    return int(random() * 0xffffffff)


class TSIDGenerator:
    def __init__(
        self,
        node: int | None = None,
        node_bits: int = 8,
        epoch: datetime | None = None,
        random_fn: t.Callable[[], int] | None = None
    ) -> None:
        """Creates a new TSID generator.

        Args:
        - `node` int | None: Node identifier. Defaults to None.
        - `node_bits` int:   Number of bytes used to repesent the node id.
                             Defaults to 8.
        - `epoch` datetime:  Epoch start. Defaults to TSID_EPOCH.
        - `randomize` bool:  Randomize counter. Defaults to True.
        - `random_fn`:       Function to use to randomize the counter.
                             Must return a 32-bit integer. If None, the
                             default `random::random()` is used to return a
                             random integer.

        > Note that not all bits of the counter are used, as the number of
          bits used to represent the node id is configurable. The number of
          bits used to represent the counter is `RANDOM_BITS - node_bits`.
        """
        self.random_fn = random_fn or _rnd_generator

        self.counter: int = self.random_fn()
        self.node: int = NODE_ID if node is None else node
        self.epoch: datetime = epoch or TSID_EPOCH
        self._millis: float = datetime.now().timestamp() * 1000

        self._node_bits: int = node_bits
        self._counter_bits: int = RANDOM_BITS - node_bits
        self._counter_mask: int = RANDOM_MASK >> node_bits
        self._node_mask: int = RANDOM_MASK >> self._counter_bits
        
        self._lock = threading.Lock()

    def create(self) -> TSID:
        """
        >>> ### Test node extraction ------------------------------
        >>> tc = TSIDGenerator(node=255, node_bits=8)
        >>> t = tc.create()
        >>> ((t.number & RANDOM_MASK) >> tc._counter_bits) == 255
        True
        >>> tc = TSIDGenerator(node=64, node_bits=8)
        >>> t = tc.create()
        >>> ((t.number & RANDOM_MASK) >> tc._counter_bits) == 64
        True
        >>> tc = TSIDGenerator(node=512, node_bits=10)
        >>> t = tc.create()
        >>> ((t.number & RANDOM_MASK) >> tc._counter_bits) == 512
        True

        >>> ### Test counter extraction ------------------------------
        >>> tc = TSIDGenerator(node=64, node_bits=8, random_fn=lambda: 0)
        >>> t = tc.create()
        >>> t.number & tc._counter_mask == 1
        True
        >>> t = tc.create()
        >>> t.number & tc._counter_mask == 2
        True

        >>> ### Test random extraction ------------------------------
        >>> tc = TSIDGenerator(node=0, node_bits=0, random_fn=lambda: 0)
        >>> t = tc.create()
        >>> t.random == 1
        True
        >>> t = tc.create()
        >>> t.random == 2
        True

        >>> ### Test datetime extraction ------------------------------
        >>> from datetime import datetime
        >>> t = tc.create()
        >>> (t.datetime - datetime.now()).total_seconds() < 1
        True
        """
        with self._lock:
            current_millis: float = datetime.now().timestamp() * 1000

            reset_counter: bool = False

            # If not in the same millisecond, reset counter
            if int(current_millis) == int(self._millis):
                self.counter += 1

                # If the counter overflows, go to the next millisecond
                if self.counter >> self._counter_bits != 0:
                    reset_counter = True
                    self._millis += 1
            else:
                reset_counter = True
                self._millis = current_millis

            if reset_counter:
                self.counter = self.random_fn() & self._counter_mask

            millis = int(self._millis - _TSID_EPOCH_MILLIS) << RANDOM_BITS
            node = (self.node & self._node_mask) << self._counter_bits
            counter = self.counter & self._counter_mask
            return TSID(millis + node + counter)


_default_generator =TSIDGenerator(node=0, node_bits=0)
