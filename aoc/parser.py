"""HTML parsing helpers using BeautifulSoup.

Functions return plain Python types and raise InputNotFoundError / FormNotFoundError when
expected content is missing.
"""

from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

from .errors import InputNotFoundError, FormNotFoundError


def _find_tag(elem, name: str) -> Tag | None:
    found = elem.find(name)
    return found if isinstance(found, Tag) else None


def extract_input(html: str) -> str:
    """Extract puzzle input text from a problem page HTML.

    AoC renders the input at `pre` inside the `.day-instructions` or directly as the response of the /input endpoint.
    We'll search for a `<pre><code>` or a `<pre>` block.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try common locations
    pre = soup.find("pre")
    if not pre:
        raise InputNotFoundError("Could not find puzzle input in page HTML")

    return pre.get_text()


def extract_level(html: str) -> Optional[int]:
    """Extract hidden input level value from the form, if present.

    Returns int or None if not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    inp = soup.find("input", attrs={"type": "hidden", "name": "level"})
    if not isinstance(inp, Tag):
        return None

    val = inp.get("value")
    if not isinstance(val, str):
        return None

    try:
        return int(val)
    except Exception:
        return None


class SubmissionResult:
    """Structured result from parsing the response HTML of a submission."""

    kind: str
    message: str

    def __init__(self, kind: str, message: str):
        self.kind = kind
        self.message = message

    def __repr__(self) -> str:  # pragma: no cover - convenience
        return f"SubmissionResult(kind={self.kind!r}, message={self.message!r})"


def parse_submission_response(html: str) -> SubmissionResult:
    """Parse the server response HTML after submitting an answer."""
    soup = BeautifulSoup(html, "html.parser")

    article = _find_tag(soup, "article")
    if article is None:
        main = _find_tag(soup, "main")
        if main is not None:
            article = _find_tag(main, "article")

    text = article.get_text(separator=" ").strip() if article else ""
    lowered = text.lower()

    # Order matters: check for exact success phrase first
    if "that's the right answer" in lowered:
        return SubmissionResult("correct", text)

    if "that's not the right answer" in lowered:
        return SubmissionResult("wrong", text)

    # Already completed / form missing: treat as completed if a level input is absent and page shows no form
    # Caller is expected to check for form separately; here we use a fallback
    if not _find_tag(soup, "input") or not soup.find("input", attrs={"name": "level"}):
        return SubmissionResult("no_form", text or "No submission form found on page")

    # Unknown fallback
    return SubmissionResult("unknown", text or "No recognizable message found")
