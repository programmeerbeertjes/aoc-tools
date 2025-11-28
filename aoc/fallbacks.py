"""
Fallback system for resolving parameters in API functions.

Each parameter can have a chain of fallback functions, similar in
style to Click's @option decorators.

Usage:

    @param_fallback("day", env_int, config, today)
    @param_fallback("cookie", env, config, error)
    def func(day=None, cookie=None):
        ...

The decorator modifies the function so that each decorated parameter
will try its fallback functions *if and only if* its call-site value
is None.
"""

import os
from functools import wraps
from inspect import signature
from datetime import date
from typing import Any, Callable, Optional

from . import config as _config
from .errors import MissingCookieError

# ============================================================
# Fallback helpers
# ============================================================

def env(name: str) -> Optional[str]:
    """Return environment variable AOC_<NAME> if present, else None."""
    key = f"AOC_{name.upper()}"
    return os.environ.get(key)


def env_int(name: str) -> Optional[int]:
    """Environment variable but parsed as int, returning None on absence."""
    value = env(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable AOC_{name.upper()} must be an int")


def config(name: str) -> Optional[Any]:
    """Read from aoc.config (simple attribute lookup)."""
    return getattr(_config, name, None)


def today(name: str) -> int:
    """Fallback to today's date.year or date.day."""
    if name not in ("year", "day"):
        raise ValueError(f"'today' fallback is only valid for 'year' or 'day'")

    value = getattr(date.today(), name)
    print(f"[aoc] Warning: no {name} supplied — falling back to today.{name}={value}")
    return value


def cookie_error(name: str):
    """Final fallback that always raises."""
    raise MissingCookieError("Personal cookie not provided, and no AOC_COOKIE envvar or config value present")


# ============================================================
# param_fallback decorator
# ============================================================

def param_fallback(param_name: str, *fallbacks: Callable[[str], Any]):
    """
    Decorator: specify a fallback chain for the parameter `param_name`.

    Each fallback is a function that takes (param_name) and returns:
        - a resolved value, or
        - None to indicate "not found", and the next fallback is tried.

    The decorated function will:
        - keep explicit arguments exactly as passed
        - resolve None arguments using fallbacks
        - resolve missing keyword arguments (if the function has defaults)
    """

    def decorator(func):
        sig = signature(func)

        if param_name not in sig.parameters:
            raise ValueError(
                f"param_fallback: function '{func.__name__}' "
                f"has no parameter named '{param_name}'"
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            # Get the explicit value (may be None).
            explicit = bound.arguments.get(param_name)

            # If explicitly provided and not None -> skip fallback
            if explicit is not None:
                return func(*args, **kwargs)

            # Otherwise run fallback chain
            for fb in fallbacks:
                out = fb(param_name)
                if out is not None:
                    bound.arguments[param_name] = out
                    break
            else:
                # All fallbacks failed: leave as None
                pass

            return func(*bound.args, **bound.kwargs)

        return wrapper

    return decorator
