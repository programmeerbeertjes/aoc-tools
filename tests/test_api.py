import pytest
from unittest.mock import patch, Mock
from aoc.api import fetch, submit
from aoc.errors import InputNotFoundError, WrongAnswerError, FormNotFoundError


# This is trivial: remove
@patch("aoc.client.fetch_input", return_value="ABC")
def test_fetch_success(mock_fetch_input):
    result = fetch(year=2023, day=1)
    assert result == "ABC"

# This should not be a functionality: remove
@patch("aoc.client.fetch_input", side_effect=Exception("not available"))
@patch("aoc.client.fetch_page", return_value="<pre>XYZ</pre>")
def test_fetch_fallback(mock_fetch_page, mock_fetch_input):
    result = fetch(year=2023, day=1)
    assert result == "XYZ"

@patch("aoc.client.fetch_input", side_effect=Exception("oops"))
@patch("aoc.client.fetch_page", return_value="<html>No input</html>")
def test_fetch_missing(mock_fetch_page, mock_fetch_input):
    with pytest.raises(InputNotFoundError):
        fetch(year=2023, day=1)

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
