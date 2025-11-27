import pytest
from aoc.parser import extract_level, parse_submission_response, extract_code, extract_example

def test_extract_level_found():
    html = '<form><input type="hidden" name="level" value="2" /></form>'
    assert extract_level(html) == 2

def test_extract_level_missing():
    html = '<html>No level</html>'
    assert extract_level(html) is None

def test_parse_submission_correct():
    html = '<article>That\'s the right answer!</article>'
    res = parse_submission_response(html)
    assert res.kind == "correct"

def test_parse_submission_wrong():
    html = '<article>That\'s not the right answer; try again.</html>'
    res = parse_submission_response(html)
    assert res.kind == "wrong"

def test_parse_submission_no_form():
    html = '<article>Some text</article>'
    res = parse_submission_response(html)
    assert res.kind == "no_form"

def test_extract_code_single():
    html = '<pre><code>ABC123</code></pre>'
    assert extract_code(html, idx=0) == "ABC123"
    assert extract_code(html) == "ABC123"

def test_extract_code_multiple():
    html = '<pre><code>AAA</code></pre><pre><code>BBB</code></pre>'
    result = extract_code(html)
    assert "AAA" in result
    assert "BBB" in result

def test_extract_example_basic():
    html = '<p>Some text for this example: (details)</p><pre><code>XYZ</code></pre>'
    assert extract_example(html, idx=0) == "XYZ"

def test_extract_example_no_match():
    html = '<p>Nothing here</p><pre><code>ABC</code></pre>'
    result = extract_example(html)
    assert result == ""
