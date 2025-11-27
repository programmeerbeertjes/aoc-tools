"""HTML parsing helpers using BeautifulSoup for AoC.

Functions return plain Python types and raise FormNotFoundError / InputNotFoundError
when expected content is missing.
"""

from __future__ import annotations

from typing import Optional, Union
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from .errors import FormNotFoundError


def _find_tag(elem, name: str) -> Optional[Tag]:
    found = elem.find(name)
    return found if isinstance(found, Tag) else None


def extract_level(html: str) -> Optional[int]:
    """Extract hidden input level value from the form, if present."""
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


def extract_code(html: str, idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Extract <pre><code> blocks from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    blocks = [code.get_text() for code in soup.find_all("code") if code.parent.name == "pre"]
    
    if idx is not None:
        try:
            return blocks[idx]
        except IndexError:
            raise IndexError(f"No code block at {idx=}")

    return sep.join(blocks)


def extract_example(html: str, idx: Optional[int] = None, sep: str = "\n") -> Union[str, list[str]]:
    """Extract <pre><code> blocks immediately preceded by a <p> containing 'for example:'."""
    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    for pre in soup.find_all("pre"):
        code = pre.find("code")
        if code is None:
            continue
        prev = pre.find_previous_sibling("p")
        if prev is None:
            continue
        # Flexible spacing and any text
        text = prev.get_text()
        if re.search(r".*for.*example.*:.*", text, re.I):
            candidates.append(code.get_text())

    if idx is not None:
        try:
            return candidates[idx]
        except IndexError:
            raise IndexError(f"No example block at {idx=}")
    return sep.join(candidates)


class SubmissionResult:
    kind: str
    message: str

    def __init__(self, kind: str, message: str):
        self.kind = kind
        self.message = message

    def __repr__(self) -> str:
        return f"SubmissionResult(kind={self.kind!r}, message={self.message!r})"


def parse_submission_response(html: str) -> SubmissionResult:
    """Parse AoC submission response HTML."""
    soup = BeautifulSoup(html, "html.parser")
    article = _find_tag(soup, "article")
    if article is None:
        main = _find_tag(soup, "main")
        if main is not None:
            article = _find_tag(main, "article")
    text = article.get_text(separator=" ").strip() if article else ""
    lowered = text.lower()

    if "that's the right answer" in lowered:
        return SubmissionResult("correct", text)
    if "that's not the right answer" in lowered:
        return SubmissionResult("wrong", text)
    if not _find_tag(soup, "input") or not soup.find("input", attrs={"name": "level"}):
        return SubmissionResult("no_form", text or "No submission form found on page")
    return SubmissionResult("unknown", text or "No recognizable message found")
