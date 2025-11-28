import pytest
from click.testing import CliRunner
from unittest.mock import patch
from aoc.cli import cli
from aoc import config

@pytest.fixture
def runner():
    return CliRunner()

@patch("aoc.api.fetch_input", return_value="INPUT")
def test_cli_fetch_input(mock_fetch, runner):
    result = runner.invoke(cli, ["fetch", "input", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "INPUT" in result.output

@patch("aoc.api.fetch_code", return_value="CODE")
def test_cli_fetch_code(mock_fetch, runner):
    result = runner.invoke(cli, ["fetch", "code", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "CODE" in result.output

@patch("aoc.api.fetch_example", return_value="EXAMPLE")
def test_cli_fetch_example(mock_fetch, runner):
    result = runner.invoke(cli, ["fetch", "example", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "EXAMPLE" in result.output

@patch("aoc.api.submit", return_value="OK")
def test_cli_submit_single(mock_submit, runner):
    result = runner.invoke(cli, ["submit", "1234", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "OK" in result.output

@patch("aoc.api.submit", return_value="First OK\nSecond OK")
def test_cli_submit_two(mock_submit, runner):
    result = runner.invoke(cli, ["submit", "1111", "2222", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "First OK\nSecond OK" in result.output

def test_cli_submit_no_input(runner):
    result = runner.invoke(cli, ["submit"])
    assert result.exit_code == 2

@patch("aoc.api.submit", return_value="OK")
def test_cli_submit_single_stdin(mock_submit, runner):
    result = runner.invoke(cli, ["submit", "--year", "2023", "--day", "5"], input="1234\n")
    assert result.exit_code == 0
    assert "OK" in result.output

@patch("aoc.api.submit", return_value="First OK\nSecond OK")
def test_cli_submit_two_stdin(mock_submit, runner):
    result = runner.invoke(cli, ["submit", "--year", "2023", "--day", "5"], input="1111\n2222\n")
    assert result.exit_code == 0
    assert "First OK\nSecond OK" in result.output

def test_cli_submit_no_answers(runner):
    result = runner.invoke(cli, ["submit", "--year", "2023", "--day", "5"])
    assert result.exit_code == 2
    assert "No answers provided" in result.output

def test_cli_submit_stdin_and_manual(runner):
    result = runner.invoke(cli, ["submit", "1234", "--year", "2023", "--day", "5"], input="1111\n")
    assert result.exit_code == 2
    assert "Cannot mix" in result.output

def test_cli_submit_three_stdin(runner):
    result = runner.invoke(cli, ["submit"], input="1\n2\n3\n")
    assert result.exit_code == 2
    assert "Too many answers" in result.output

@patch("aoc.api.fetch_input", return_value="INPUT")
def test_cli_fetch_input_today(mock_fetch, runner):
    result = runner.invoke(cli, ["fetch", "input", "--date", "today"])
    assert result.exit_code == 0
    assert "INPUT" in result.output

@patch("aoc.api.submit", return_value="OK")
def test_cli_submit_today(mock_submit, runner):
    result = runner.invoke(cli, ["submit", "1234", "--date", "today"])
    assert result.exit_code == 0
    assert "OK" in result.output
