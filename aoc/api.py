"""Public Python API: fetch() and submit().

Raise the exceptions defined in errors.py on failure.
"""

from __future__ import annotations

from typing import Optional

from . import client, parser
from .errors import (
    AOCError,
    FormNotFoundError,
    InputNotFoundError,
    MissingCookieError,
    WrongAnswerError,
    AlreadyCompletedError,
)


def fetch(year: Optional[int] = None, day: Optional[int] = None) -> str:
    """Fetch puzzle input for the given year/day and return as string.

    Raises InputNotFoundError or MissingCookieError.
    """
    try:
        # Use the dedicated endpoint which returns plain text
        return client.fetch_input(year, day)
    except MissingCookieError:
        raise
    except Exception as exc:
        # Try fallback: fetch page and parse pre block
        try:
            html = client.fetch_page(year, day)
            return parser.extract_input(html)
        except Exception as exc2:
            raise InputNotFoundError(f"Could not fetch puzzle input: {exc2}") from exc


def submit(answer: str | int, year: Optional[int] = None, day: Optional[int] = None, part: Optional[int] = None) -> str:
    """Submit an answer and return the server message on success.

    Raises:
      - FormNotFoundError
      - WrongAnswerError
      - RateLimitError
      - AlreadyCompletedError
      - MissingCookieError
      - AOCError for other errors
    """
    # normalize
    answer_str = str(answer)

    # Ensure we have year/day
    year, day = client._default_year_day(year, day)

    level = part
    if level is None:
         # Fetch page HTML to learn the current form/level
        page_html = client.fetch_page(year, day)
        level = parser.extract_level(page_html)

    if level is None:
        # No form available; either you already solved it or cannot submit
        raise FormNotFoundError("No submission form present for this puzzle/part")

    # Post the answer
    resp_html = client.submit_answer(answer_str, year=year, day=day, level=level)

    # Parse response
    result = parser.parse_submission_response(resp_html)

    if result.kind == "correct":
        return result.message
    if result.kind == "wrong":
        raise WrongAnswerError(result.message)
    if result.kind == "no_form":
        raise AlreadyCompletedError(result.message)

    # fallback
    raise AOCError(result.message)
