# Change Log

All notable changes to "aoc-tools" will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-26

- Initial release.

### Added

- Python and command line interface (under `aoc`) for AoC input fetching and answer submission.
- Test suite under `tests` directory.

## [0.2.0] - 2025-11-27

### Added

- Parsers for code blocks and examples in the puzzle input HTML
- Extra tests for the above functionality.
- MIT license and this changelog file.

### Changed

- Split `aoc fetch` CLI command into `aoc fetch input`, `aoc fetch code` and `aoc fetch example`.
- Update README with above functionality.

### Removed

- Fallback for input parser from the puzzle HTML. Fetching input will always look in the puzzle URL with the `/input` suffix.

## [0.3.0] - 2025-11-27

### Changed

- Command `aoc fetch` and its Python equivalent can take two answers. See usage in the README for more details.

## [0.3.1] - 2025-11-27

### Added

- Local configuration file `.aoc.toml` for setting year, day, and cookie
- A new `aoc config` command to create, change, and clear this config.
- A new `--date` option on all CLI commands, which can be supplied a string in the format `YYYY/DD`, `YYYY/D` or the literal `today`

### Changed

- The `client.py` no longer accepts optional `year` or `day`.

