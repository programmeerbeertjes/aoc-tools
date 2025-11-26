"""Public API for the aoc package.

Expose fetch() and submit() functions for direct import.
"""

from .api import fetch, submit

# Used for * imports
__all__ = ["fetch", "submit"]
