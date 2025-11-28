"""Public Python API: fetch_input(), fetch_code(), fetch_example(), and submit().

Raise the exceptions defined in errors.py on failure.
"""
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
    UnknownDateError,
)
from .fallbacks import param_fallback, env_int, env, config, today, cookie_error


# ------------------------------
# Fetching puzzle data
# ------------------------------
@param_fallback("year", env_int, config, today)
@param_fallback("day", env_int, config, today)
@param_fallback("cookie", env, config, cookie_error)
def fetch_input(year: Optional[int] = None, day: Optional[int] = None, cookie: Optional[str] = None) -> str:
    """Fetch puzzle input via /input endpoint; always plain text."""
    if year is None or day is None:
        raise UnknownDateError("Puzzle year or day not set")

    if cookie is None:
        raise MissingCookieError("Personal cookie not provided, and no AOC_COOKIE envvar or config value present")

    try:
        return client.fetch_input(year, day, cookie)
    except Exception as exc:
        raise InputNotFoundError(f"Could not fetch puzzle input: {exc}") from exc


@param_fallback("year", env_int, config, today)
@param_fallback("day", env_int, config, today)
def fetch_code(year: Optional[int] = None, day: Optional[int] = None,
               idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Fetch <pre><code> blocks from the problem page."""
    if year is None or day is None:
        raise UnknownDateError("Puzzle year or day not set")
    
    html = client.fetch_page(year, day)
    return parser.extract_code(html, idx=idx, sep=sep)


@param_fallback("year", env_int, config, today)
@param_fallback("day", env_int, config, today)
def fetch_example(year: Optional[int] = None, day: Optional[int] = None,
                  idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Fetch example <pre><code> blocks preceded by 'for example:' <p>."""
    if year is None or day is None:
        raise UnknownDateError("Puzzle year or day not set")

    html = client.fetch_page(year, day)
    return parser.extract_example(html, idx=idx, sep=sep)


# ------------------------------
# Submit answers
# ------------------------------
@param_fallback("year", env_int, config, today)
@param_fallback("day", env_int, config, today)
@param_fallback("cookie", env, config, cookie_error)
def submit(first_answer: str | int,
           second_answer: Optional[str | int] = None,
           /,
           year: Optional[int] = None,
           day: Optional[int] = None,
           cookie: Optional[str] = None) -> str:
    """Submit one or two answers to AoC.

    If one answer is supplied, submits to the given puzzle as whichever
    part is not solved yet.

    If two answers are supplied, they are submitted one after the other
    with 1s in between. If the first part has been solved, only submit
    the second answer.
    """
    if year is None or day is None:
        raise UnknownDateError("Puzzle year or day not set")

    if cookie is None:
        raise MissingCookieError("Personal cookie not provided, and no AOC_COOKIE envvar or config value present")

    html = client.fetch_page(year, day)
    level = parser.extract_level(html)

    if level is None:
        raise FormNotFoundError("No submission form present for this puzzle/part")

    def submit_single(answer: str | int, level: int) -> str:
        resp_html = client.submit_answer(str(answer), year, day, level, cookie)
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
