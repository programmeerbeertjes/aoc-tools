"""HTTP client utilities for AoC.

Responsibilities:
- Read cookie from AOC_COOKIE env var (required)
- Fetch page HTML
- Fetch puzzle input text
- Submit an answer

This module purposely avoids interpreting HTML; it returns raw text for parser.py to handle.
"""

import requests

BASE = "https://adventofcode.com"


def fetch_page(year: int, day: int) -> str:
    """GET the AoC problem page HTML for year/day (authenticated).

    Returns raw HTML string. Cookie not necessary.
    """
    url = f"{BASE}/{year}/day/{day}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text


def fetch_input(year: int, day: int, cookie: str) -> str:
    """GET the raw puzzle input for year/day (authenticated).

    Returns the plain text input body. Cookie-specific.
    """
    url = f"{BASE}/{year}/day/{day}/input"
    resp = requests.get(url, cookies={"session": cookie})
    resp.raise_for_status()
    return resp.text


def submit_answer(answer: str, year: int, day: int, level: int, cookie: str) -> str:
    """POST an answer to AoC and return the response HTML.
    
    Callers should specify a level parameter (which puzzle part to send).
    """
    url = f"{BASE}/{year}/day/{day}/answer"
    data = {"level": str(level), "answer": str(answer)}
    resp = requests.post(url, cookies={"session": cookie}, data=data)
    resp.raise_for_status()
    return resp.text
