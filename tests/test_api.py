import pytest
from unittest.mock import patch
from aoc.api import fetch_input, fetch_code, fetch_example, submit
from aoc.errors import InputNotFoundError, WrongAnswerError, FormNotFoundError

@patch("aoc.client.fetch_input", return_value="ABC")
def test_fetch_input(mock_fetch):
    assert fetch_input(2023,1) == "ABC"

@patch("aoc.client.fetch_page", return_value='<pre><code>AAA</code></pre>')
def test_fetch_code_idx(mock_page):
    assert fetch_code(2023,1, idx=0) == "AAA"

@patch("aoc.client.fetch_page", return_value='<pre><code>AAA</code></pre><pre><code>BBB</code></pre>')
def test_fetch_code_all(mock_page):
    result = fetch_code(2023,1)
    assert "AAA" in result and "BBB" in result

@patch("aoc.client.fetch_page", return_value='<p>Intro for example:</p><pre><code>XYZ</code></pre>')
def test_fetch_example_idx(mock_page):
    assert fetch_example(2023,1, idx=0) == "XYZ"

@patch("aoc.client.fetch_page", return_value='<p>Intro for example:</p><pre><code>XYZ</code></pre><p>For another example:</p><pre><code>123</code></pre>')
def test_fetch_example_all(mock_page):
    result = fetch_example(2023,1)
    assert "XYZ" in result and "123" in result

@patch("aoc.client.fetch_page", return_value="<form><input type='hidden' name='level' value='2'></form>")
@patch("aoc.client.submit_answer", return_value="<article><p>That's the right answer!</p></article>")
def test_submit_correct(mock_submit_answer, mock_get_day_html):
    result = submit(1234, year=2023, day=1)
    assert result == "That's the right answer!"

@patch("aoc.client.fetch_page", return_value="<form><input type='hidden' name='level' value='2'></form>")
@patch("aoc.client.submit_answer", return_value="<article><p>That's not the right answer</p></article>")
def test_submit_wrong_answer(mock_submit_answer, mock_get_day_html):
    with pytest.raises(WrongAnswerError):
        submit(9999, year=2023, day=1)

@patch("aoc.client.fetch_page", return_value="<html><body>No form here</body></html>")
def test_submit_no_form(mock_get_day_html):
    with pytest.raises(FormNotFoundError):
        submit(1111, year=2023, day=1)
