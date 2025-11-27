"""Public Python API: fetch_input(), fetch_code(), fetch_example(), and submit().

Raise the exceptions defined in errors.py on failure."""

from __future__ import annotations
from time import sleep
from typing import Optional, Union

from . import client, parser
from .errors import (
    AOCError,
    FormNotFoundError,
    InputNotFoundError,
    MissingCookieError,
    WrongLevelError,
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


def submit(first_answer: str | int, second_answer: Optional[str | int] = None, /, year: Optional[int] = None, day: Optional[int] = None) -> str:
    """Submit one or two answers to AoC.

    If one answer is supplied, submits to the given puzzle as whichever
    part is not solved yet.

    If two answers are supplied, they are submitted one after the other
    with 1s in between. If the first part has been solved, only submit
    the second answer.
    """
    html = client.fetch_page(year, day)
    level = parser.extract_level(html)

    if level is None:
        raise FormNotFoundError("No submission form present for this puzzle/part")

    def submit_single(answer: str | int, level: int) -> str:
        resp_html = client.submit_answer(str(answer), level, year=year, day=day)
        result = parser.parse_submission_response(resp_html)

        if result.kind == "correct":
            return result.message
        if result.kind == "wrong":
            raise WrongAnswerError(result.message)
        if result.kind == "incorrect_level":
            raise WrongLevelError(result.message)
        if result.kind == "no_form":
            raise AlreadyCompletedError(result.message)
        raise AOCError(result.message)

    if second_answer is None:
        return submit_single(first_answer, level)

    # Level 2: skip first answer
    if level == 2:
        return submit_single(second_answer, level)
    
    # Two answers
    msg1 = submit_single(first_answer, level)
    sleep(1)
    msg2 = submit_single(second_answer, level + 1)
    return "\n".join([msg1, msg2])
