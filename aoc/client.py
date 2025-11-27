"""HTTP client utilities for AoC.

Responsibilities:
- Read cookie from AOC_COOKIE env var (required)
- Fetch page HTML
- Fetch puzzle input text
- Submit an answer

This module purposely avoids interpreting HTML; it returns raw text for parser.py to handle.
"""

from __future__ import annotations

import os
from typing import Optional
import datetime

import requests

from .errors import MissingCookieError

BASE = "https://adventofcode.com"


def _get_cookie() -> str:
    cookie = os.getenv("AOC_COOKIE")
    if not cookie:
        raise MissingCookieError("Environment variable AOC_COOKIE not set")
    return cookie


def _default_year_day(year: Optional[int], day: Optional[int]) -> tuple[int, int]:
    if year is None or day is None:
        today = datetime.date.today()
    if year is None:
        year = int(os.getenv("AOC_YEAR", today.year))
    if day is None:
        day = int(os.getenv("AOC_DAY", today.day))
    return year, day


def fetch_page(year: Optional[int] = None, day: Optional[int] = None) -> str:
    """GET the AoC problem page HTML for year/day (authenticated).

    Returns raw HTML string.
    """
    year, day = _default_year_day(year, day)
    url = f"{BASE}/{year}/day/{day}"
    resp = requests.get(url, cookies={"session": _get_cookie()})
    resp.raise_for_status()
    return resp.text


def fetch_input(year: Optional[int] = None, day: Optional[int] = None) -> str:
    """GET the raw puzzle input for year/day (authenticated).

    Returns the plain text input body.
    """
    year, day = _default_year_day(year, day)
    url = f"{BASE}/{year}/day/{day}/input"
    resp = requests.get(url, cookies={"session": _get_cookie()})
    resp.raise_for_status()
    return resp.text


def submit_answer(answer: str, level: int, year: Optional[int] = None, day: Optional[int] = None) -> str:
    """POST an answer to AoC and return the response HTML.
    
    Callers should specify a level parameter (which puzzle part to send).
    """
    year, day = _default_year_day(year, day)
    url = f"{BASE}/{year}/day/{day}/answer"
    data = {"level": str(level), "answer": str(answer)}
    resp = requests.post(url, cookies={"session": _get_cookie()}, data=data)
    resp.raise_for_status()
    return resp.text
