# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Automated `pytest` coverage for the public API, deterministic generator behavior, doctests, and opt-in performance benchmarks.

### Changed

- Reduced `TSIDGenerator` hot-path overhead by shrinking the locked section and precomputing the fixed node bit segment.
- Optimized generic base decoding by replacing repeated `ALPHABET.index()` lookups with a precomputed lookup table.
- Added fast hexadecimal paths for `TSID.to_string('X'/'x')` and `TSID.from_string('X'/'x')`.

### Performance

- Local `perf` benchmark results on `macOS-15.7.3-arm64-arm-64bit`:
  - `tsid_from_string_X` improved from about `0.66M ops/s` to about `3.43M ops/s`.
  - `tsid_to_string_X` improved from about `0.82M ops/s` to about `4.18M ops/s`.
  - Shared-generator throughput improved from about `1.58M ops/s` to about `1.68M ops/s` in the 1-thread case, with similar throughput retained under multi-thread contention.

## [1.1.5] - 2023-11-28

### Added

- Make `TSID` values hashable.

## [1.1.4] - 2023-11-09

### Added

- `datetime` property.

## [1.1.3] - 2023-10-09

### Fixed

- Honor Python 3.7 syntax .

## [1.1.2] - 2023-09-13

### Fixed

- Properly exported symbols as per https://github.com/microsoft/pylance-release/issues/2953#issuecomment-1168408943.

## [1.1.1] - 2023-08-18

### Added

- Package type hints (thanks to https://github.com/kasium) (#2).
- `CHANGELOG.md` file and proper semver schema adhesion (#3).
