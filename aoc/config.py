import os
from pathlib import Path
from typing import Optional, Any

import toml

CONFIG_FILENAME = ".aoc.toml"


def find_config_file(start: Optional[Path] = None) -> Optional[Path]:
    """
    Search upward from `start` (or cwd) for the nearest CONFIG_FILENAME.
    Returns the Path of the first found file, or None if not found.
    """
    if start is None:
        start = Path.cwd()

    start = start.resolve()
    for directory in [start, *start.parents]:
        candidate = directory / CONFIG_FILENAME
        if candidate.exists():
            return candidate

    return None


class _Config:
    """
    Lightweight config manager backed by a flat TOML file.
    Public API (singleton instance `config`) exposes:
      - config.year (getter/setter/deleter)
      - config.day  (getter/setter/deleter)
      - config.cookie (getter/setter/deleter)
      - config.date (getter returns (year, day); setter accepts tuple only)
      - config.clear()
      - config.list() -> dict
    """

    def __init__(self, path=None):
        # If a config file exists upwards, remember it and load data.
        self._path: Optional[Path] = find_config_file(path)
        self._data: dict[str, Any] = {}
        if self._path:
            try:
                # toml.load accepts a file path object
                self._data = toml.load(self._path)
            except Exception:
                # If parse fails, treat as empty (user can overwrite)
                self._data = {}

    # Internal helpers
    def _save(self):
        """Persist self._data to the TOML file (creating it if needed)."""
        if not self._path:
            # Create file in current directory
            self._path = Path.cwd() / CONFIG_FILENAME

        with open(self._path, "w", encoding="utf8") as f:
            toml.dump(self._data, f)

    def _get(self, key: str):
        return self._data.get(key)

    def _set(self, key: str, value):
        if value is None:
            self._data.pop(key, None)
        else:
            self._data[key] = value
        self._save()

    def _del(self, key: str):
        self._data.pop(key, None)
        self._save()

    # Public properties
    @property
    def year(self) -> Optional[int]:
        v = self._get("year")
        return int(v) if v is not None else None

    @year.setter
    def year(self, value: int):
        if os_env := os.environ.get("AOC_YEAR"):
            print(f"[aoc] Warning: AOC_YEAR={os_env} env is set; it overrides config.year")
        self._set("year", value)

    @year.deleter
    def year(self):
        self._del("year")

    @property
    def day(self) -> Optional[int]:
        v = self._get("day")
        return int(v) if v is not None else None

    @day.setter
    def day(self, value: int):
        if os_env := os.environ.get("AOC_DAY"):
            print(f"[aoc] Warning: AOC_DAY={os_env} env is set; it overrides config.day")
        self._set("day", value)

    @day.deleter
    def day(self):
        self._del("day")

    @property
    def cookie(self) -> Optional[str]:
        v = self._get("cookie")
        return str(v) if v is not None else None

    @cookie.setter
    def cookie(self, value: str):
        self._set("cookie", value)

    @cookie.deleter
    def cookie(self):
        self._del("cookie")

    # Synthetic date property (getter only reads explicit fields)
    @property
    def date(self) -> tuple[Optional[int], Optional[int]]:
        """
        Return the explicit (year, day) stored in the config (not resolved with env/default).
        Each can be None if not present.
        """
        return self.year, self.day

    @date.setter
    def date(self, value) -> None:
        """
        Accept only an explicit tuple (year, day).
        The CLI is responsible for parsing strings like 'today' or 'YYYY/D'.
        """
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError("config.date setter accepts only a (year, day) tuple")
        y, d = value
        if y is None or d is None:
            raise ValueError("config.date requires both year and day integers")
        self.year = int(y)
        self.day = int(d)

    @date.deleter
    def date(self) -> None:
        self._del("year")
        self._del("day")

    # Utilities --------------------------------------------------------
    def clear(self) -> None:
        """Remove all values and persist (delete file contents)."""
        self._data.clear()
        self._save()

    def list(self) -> dict[str, Any]:
        """Return a shallow copy of the raw config data (flat keys)."""
        return dict(self._data)


# Public singleton used by the package
config = _Config()
