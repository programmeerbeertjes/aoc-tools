"""Public Python API: fetch_input(), fetch_code(), fetch_example(), and submit().

Raise the exceptions defined in errors.py on failure."""

from __future__ import annotations
from typing import Optional, Union

from . import client, parser
from .errors import (
    AOCError,
    FormNotFoundError,
    InputNotFoundError,
    MissingCookieError,
    WrongAnswerError,
    AlreadyCompletedError,
)


def fetch_input(year: Optional[int] = None, day: Optional[int] = None) -> str:
    """Fetch puzzle input via /input endpoint; always plain text."""
    try:
        return client.fetch_input(year, day)
    except MissingCookieError:
        raise
    except Exception as exc:
        raise InputNotFoundError(f"Could not fetch puzzle input: {exc}") from exc


def fetch_code(year: Optional[int] = None, day: Optional[int] = None,
               idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Fetch <pre><code> blocks from the problem page."""
    html = client.fetch_page(year, day)
    return parser.extract_code(html, idx=idx, sep=sep)


def fetch_example(year: Optional[int] = None, day: Optional[int] = None,
                  idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Fetch example <pre><code> blocks preceded by 'for example:' <p>."""
    html = client.fetch_page(year, day)
    return parser.extract_example(html, idx=idx, sep=sep)


def submit(answer: str | int, year: Optional[int] = None, day: Optional[int] = None,
           part: Optional[int] = None) -> str:
    """Submit an answer and return server message; raises errors for wrong submissions."""
    answer_str = str(answer)
    year, day = client._default_year_day(year, day)
    level = part
    if level is None:
        page_html = client.fetch_page(year, day)
        level = parser.extract_level(page_html)

    if level is None:
        raise FormNotFoundError("No submission form present for this puzzle/part")

    resp_html = client.submit_answer(answer_str, year=year, day=day, level=level)
    result = parser.parse_submission_response(resp_html)

    if result.kind == "correct":
        return result.message
    if result.kind == "wrong":
        raise WrongAnswerError(result.message)
    if result.kind == "no_form":
        raise AlreadyCompletedError(result.message)
    raise AOCError(result.message)
