"""Public API for the aoc package.

Expose fetching and submission functions for direct import.
"""

from .api import (
    fetch_input,
    fetch_code,
    fetch_example,
    submit,
)

__all__ = [
    "fetch_input",
    "fetch_code",
    "fetch_example",
    "submit",
]
