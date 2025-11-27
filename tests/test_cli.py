import pytest
from click.testing import CliRunner
from aoc.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_fetch_input(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.fetch_input", lambda year, day: "INPUT")
    result = runner.invoke(cli, ["fetch", "input", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "INPUT" in result.output

def test_cli_fetch_code(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.fetch_code", lambda year, day, idx=None, sep="\n": "CODE")
    result = runner.invoke(cli, ["fetch", "code", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "CODE" in result.output

def test_cli_fetch_example(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.fetch_example", lambda year, day, idx=None, sep="\n": "EXAMPLE")
    result = runner.invoke(cli, ["fetch", "example", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "EXAMPLE" in result.output

def test_cli_submit(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.submit", lambda answer, year=None, day=None, part=None: "Good job!")
    result = runner.invoke(cli, ["submit", "1234", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "Good job!" in result.output
