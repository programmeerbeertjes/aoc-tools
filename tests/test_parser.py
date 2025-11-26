import pytest
from aoc.parser import extract_input, extract_level, parse_submission_response, SubmissionResult
from aoc.errors import InputNotFoundError


def test_extract_input_basic():
    html = """
    <html><body>
    <pre>line1\nline2</pre>
    </body></html>
    """
    assert extract_input(html) == "line1\nline2"


def test_extract_input_missing():
    with pytest.raises(InputNotFoundError):
        extract_input("<html>No input here</html>")


def test_extract_level_found():
    html = """
    <html><body>
    <form><input type="hidden" name="level" value="2" /></form>
    </body></html>
    """
    assert extract_level(html) == 2


def test_extract_level_missing():
    html = "<html><body>No level here</body></html>"
    assert extract_level(html) is None


def test_parse_submission_correct():
    html = """
    <html><body><article>That's the right answer!</article></body></html>
    """
    res = parse_submission_response(html)
    assert res.kind == "correct"


def test_parse_submission_wrong():
    html = """
    <html><body><article>That's not the right answer; try again.</article></body></html>
    """
    res = parse_submission_response(html)
    assert res.kind == "wrong"


def test_parse_submission_no_form():
    html = """
    <html><body><article>Some text</article></body></html>
    """
    res = parse_submission_response(html)
    assert res.kind == "no_form"
