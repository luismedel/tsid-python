# tsid-python

A Python library for generating Time-Sorted Unique Identifiers (TSID) as defined in <https://github.com/f4b6a3/tsid-creator>.

This library is a port of the original Java code by [Fabio Lima](https://github.com/fabiolimace).

## Installation

```bash
pip install tsidpy
```

## What is a TSID?

The term TSID stands for (roughly) Time-Sorted ID. A TSID is a value that is formed by its creation time along with a random value.

It brings together ideas from [Twitter's Snowflake](https://github.com/twitter-archive/snowflake/tree/snowflake-2010) and [ULID Spec](https://github.com/ulid/spec).

In summary:

- Sorted by generation time.
- Can be stored as a 64-bit integer.
- Can be stored as a 13-char len string.
- String format is encoded to [Crockford's base32](https://www.crockford.com/base32.html).
- String format is URL safe, case insensitive and has no hyphens.
- Shorter than other unique identifiers, like [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier), [ULID](https://github.com/ulid/spec) and [KSUID](https://github.com/segmentio/ksuid).

## TSID Structure

A TSID has 2 components:

1. A time component (42 bits), consisting in the elapsed milliseconds since `2020-01-01 00:00:00 UTC` (this epoch can be configured)
2. A _random_ component (22 bits), containing 2 sub-parts:

    - A node identifier (can use 0 to 20 bits)
    - A counter (can use 2 to 22 bits)

    > Note: The counter length depends on the node identifier length.
    >
    > For example, if we use 10 bits for the node representation:
    >
    > - The counter is limited to 12 bits.
    > - The maximum node value is `2^10-1 = 1023`
    > - The maximum counter value is `2^12-1 = 4095`, so the maximum TSIDs that can be generated _per millisecond_ is `4096`.

This is the default TSID structure:

```text
                                            adjustable
                                           <---------->
|------------------------------------------|----------|------------|
       time (msecs since 2020-01-01)           node      counter
                42 bits                       10 bits    12 bits

- time:    2^42 = ~69 to ~139 years with adjustable epoch (see notes below)
- node:    up to 2^20 values with adjustable bits.
- counter: 2^2..2^22 with adjustable bits and randomized values every millisecond.
```

> Notes:
>
> - The time component can be used for ~69 years if stored in a `SIGNED 64-bit` integer field (41 usable bits) or ~139 years if stored in a `UNSIGNED 64-bit` integer field (42 usable bits).
> - By default, new TSID generators use 10 bits for the node identifier and 12 bits to the counter. It's possible to adjust the node identifier length to a value between 0 and 20.
> - The time component can be 1 ms or more ahead of the system time when necessary to maintain monotonicity and generation speed.

### Node identifier

The simplest way to avoid collisions is to make sure that each generator has an exclusive node ID.

The node ID can be passed to the `TSIDGenerator` constructor. If no node ID is passed, the generator will use a random value.

### Recommended readings

- [The best UUID type for a database Primary Key](https://vladmihalcea.com/uuid-database-primary-key/)
- [The primary key dilemma: ID vs UUID and some practical solutions](https://fillumina.wordpress.com/2023/02/06/the-primary-key-dilemma-id-vs-uuid-and-some-practical-solutions/)
- [Primary keys in the DB - what to use? ID vs UUID or is there something else?](https://www.linkedin.com/pulse/primary-keys-db-what-use-id-vs-uuid-something-else-lucas-persson)

Related with the [original library](https://github.com/f4b6a3/tsid-creator):

- [FAQ wiki page](https://github.com/f4b6a3/tsid-creator/wiki)
- [Javadocs](https://javadoc.io/doc/com.github.f4b6a3/tsid-creator)
- [How to not use TSID factories](https://fillumina.wordpress.com/2023/01/19/how-to-not-use-tsid-factories/)
- [The best way to generate a TSID entity identifier with JPA and Hibernate](https://vladmihalcea.com/tsid-identifier-jpa-hibernate/)

## Basic usage

Create a TSID:

```python
from tsidpy import TSID

tsid: TSID = TSID.create()
```

Create a TSID as an `int`:

```python
>>> TSID.create().number
432511671823499267
```

Create a TSID as a `str`:

```python
>>> str(TSID.create())
'0C04Q2BR40003'
```

Create a TSID as an hexadecimal `str`:

```python
>>> TSID.create().to_string('x')
'06009712f0400003'
```

> Note: TSID generators are [thread-safe](https://en.wikipedia.org/wiki/Thread_safety).

### TSID as int

The `TSID::number` property simply unwraps the internal `int` value of a TSID.

```python
>>> from tsidpy import TSID
>>> TSID.create(432511671823499267).number
432511671823499267
```

Sequence of TSIDs:

```text
38352658567418867
38352658567418868
38352658567418869
38352658567418870
38352658567418871
38352658567418872
38352658567418873
38352658567418874
38352658573940759 < millisecond changed
38352658573940760
38352658573940761
38352658573940762
38352658573940763
38352658573940764
38352658573940765
38352658573940766
         ^      ^ look
                                   
|--------|------|
   time   random
```

### TSID as str

The `TSID::to_string()` method encodes a TSID as a [Crockford's base 32](https://www.crockford.com/base32.html) string. The returned string is 13 characters long.

```python
>>> from tsidpy import TSID
>>> tsid: str = TSID.create().to_string()
'0C04Q2BR40004'
```

Or, alternatively:

```python
>>> tsid: str = str(TSID.create())
'0C04Q2BR40004'
```

Sequence of TSID strings:

```text
01226N0640J7K
01226N0640J7M
01226N0640J7N
01226N0640J7P
01226N0640J7Q
01226N0640J7R
01226N0640J7S
01226N0640J7T
01226N0693HDA < millisecond changed
01226N0693HDB
01226N0693HDC
01226N0693HDD
01226N0693HDE
01226N0693HDF
01226N0693HDG
01226N0693HDH
        ^   ^ look
                                   
|-------|---|
   time random
```

The string format can be useful for languages that store numbers in [IEEE 754 double-precision binary floating-point format](https://en.wikipedia.org/wiki/Double-precision_floating-point_format), such as [Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number).

### More Examples

Create a TSID using the default generator:

```python
from tsidpy import TSID

tsid: TSID = TSID.create()
```

---

Create a TSID from a canonical string (13 chars):

```python
from tsidpy import TSID

tsid: TSID = TSID.from_string('0123456789ABC')
```

---

Convert a TSID into a canonical string in lower case:

```python
>>> tsid.to_string('s')
'0123456789abc'
```

---

Get the creation `timestamp` of a TSID:

```python
>>> tsid.timestamp
1680948418241.0  # datetime.datetime(2023, 4, 8, 12, 6, 58, 241000)
```

---

Encode a TSID to base-62:

```python
>>> tsid.to_string('z')
'0T5jFDIkmmy'
```

---

A `TSIDGenerator` that creates TSIDs similar to [Twitter Snowflakes](https://github.com/twitter-archive/snowflake):

- Twitter snowflakes use 10 bits for node id: 5 bits for datacenter ID (max 31) and 5 bits for worker ID (max 31)
- Epoch starts on `2010-11-04T01:42:54.657Z`
- Counter uses 12 bits and starts at `0` (max: 4095 values per millisecond)

```python
from tsidpy import TSID, TSIDGenerator

datacenter: int = 1
worker: int = 1
node: int = datacenter << 5 | worker
epoch: datetime = datetime.fromisoformat('2010-11-04T01:42:54.657Z')

twitter_generator: TSIDGenerator = TSIDGenerator(node=node, node_bits=10,
                                                 epoch=epoch.timestamp() * 1000,
                                                 random_fn=lambda n: 0)

# use the generator
tsid: TSID = twitter_generator.create()
```

---

A `TSIDGenerator` that creates TSIDs similar to [Discord Snowflakes](https://discord.com/developers/docs/reference#snowflakes):

- Discord snowflakes use 10 bits for node id: 5 bits for worker ID (max 31) and 5 bits for process ID (max 31)
- Epoch starts on `2015-01-01T00:00:00.000Z`
- Counter uses 12 bits and starts at a random value.

```python
from tsidpy import TSID, TSIDGenerator

worker: int = 1
process: int = 1
node: int = worker << 5 | process
epoch: datetime = datetime.fromisoformat("2015-01-01T00:00:00.000Z")

discord_generator: TSIDGenerator = TSIDGenerator(node=node, node_bits=10,
                                                 epoch=epoch.timestamp() * 1000)

# use the generator
tsid: TSID = discord_generator.create()
```

---

Make `TSID.create()` to use the previous Discord generator:

```python

TSID.set_default_generator(discord_generator)

# at this point, you can use the default TSID.create()
tsid: TSID = TSID.create()

# or the generator
tsid: TSID = discord_generator.create()
```

---

### A note about node id and node bits

When creating a `TSIDGenerator`, remember you can't use a node id greater than `2^node_bits - 1`. For example, if you need to use a node id greater than 7, you need to use more than 3 bits for the node id:

```python
from tsidpy import TSIDGenerator

gen0 = TSIDGenerator(node=0, node_bis=3)  # ok
gen1 = TSIDGenerator(node=1, node_bis=3)  # ok
...
gen7 = TSIDGenerator(node=7, node_bis=3)  # ok

# error: can't represent 8 with 3 bits
gen8 = TSIDGenerator(node=8, node_bis=3)
```

## Other ports, forks and OSS

### Ports and forks

| Language | Name |
| -------- | ---- |
| Java (by original author)     | [f4b6a3/tsid-creator](https://github.com/f4b6a3/tsid-creator) |
| Java     | [vladmihalcea/hypersistence-tsid](https://github.com/vladmihalcea/hypersistence-tsid) |
| .NET     | [kgkoutis/TSID.Creator.NET](https://github.com/kgkoutis/TSID.Creator.NET) |
| PHP      | [odan/tsid](https://github.com/odan/tsid) |

### OSS

| Language | Name |
| -------- | ---- |
| Java     | [fillumina/id-encryptor](https://github.com/fillumina/id-encryptor) |
| .NET     | [ullmark/hashids.net](https://github.com/ullmark/hashids.net) |

## License

This library is Open Source software released under the [MIT license](https://opensource.org/licenses/MIT).
