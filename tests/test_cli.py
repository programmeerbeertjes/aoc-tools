import pytest
from click.testing import CliRunner
from aoc.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_fetch(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.fetch", lambda year, day: "INPUTDATA")
    result = runner.invoke(cli, ["fetch", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "INPUTDATA" in result.output


def test_cli_submit(monkeypatch, runner):
    monkeypatch.setattr("aoc.api.submit", lambda answer, year=None, day=None, part=None: "Good job!")
    result = runner.invoke(cli, ["submit", "1234", "--year", "2023", "--day", "5"])
    assert result.exit_code == 0
    assert "Good job!" in result.output
