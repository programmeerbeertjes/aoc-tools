import sys
import click
from typing import Optional

from . import api
from .errors import (
    AOCError,
    MissingCookieError,
    InputNotFoundError,
    FormNotFoundError,
    WrongLevelError,
    WrongAnswerError,
    AlreadyCompletedError,
)


@click.group()
def cli():
    """AoC CLI entry point."""
    pass


@cli.group()
def fetch():
    """Fetch puzzle input, code, or example blocks."""
    pass


@fetch.command("input")
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
def fetch_input(year: Optional[int] = None, day: Optional[int] = None):
    try:
        data = api.fetch_input(year=year, day=day)
        click.echo(data, nl=False)
    except InputNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except MissingCookieError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error fetching input: {e}", err=True)
        sys.exit(1)


@fetch.command("code")
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
@click.option('--idx', type=int, default=None, help="0-based index of code block")
@click.option('--sep', type=str, default="\n", help="Separator for multiple blocks")
def fetch_code(year: Optional[int] = None, day: Optional[int] = None,
                   idx: Optional[int] = None, sep: str = "\n"):
    try:
        data = api.fetch_code(year=year, day=day, idx=idx, sep=sep)
        click.echo(data)
    except Exception as e:
        click.echo(f"Error fetching code blocks: {e}", err=True)
        sys.exit(1)


@fetch.command("example")
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
@click.option('--idx', type=int, default=None, help="0-based index of example block")
@click.option('--sep', type=str, default="\n", help="Separator for multiple blocks")
def fetch_example(year: Optional[int] = None, day: Optional[int] = None,
                      idx: Optional[int] = None, sep: str = "\n"):
    try:
        data = api.fetch_example(year=year, day=day, idx=idx, sep=sep)
        click.echo(data)
    except Exception as e:
        click.echo(f"Error fetching example blocks: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('first_answer', required=False)
@click.argument('second_answer', required=False)
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
def submit(first_answer, second_answer, year: Optional[int] = None, day: Optional[int] = None):
    """Submit one or two answers to AoC."""

    lines = [line.strip() for line in sys.stdin if line.strip()]

    if first_answer is None and not lines:
        click.echo("No answers provided", err=True)
        sys.exit(2)

    if first_answer and lines:
        click.echo("Cannot mix command-line answers and stdin input", err=True)
        sys.exit(2)

    if len(lines) > 2:
        click.echo("Too many answers; expected 1 or 2", err=True)
        sys.exit(2)

    # If no arguments, read lines from stdin and strip blank lines
    if first_answer is None:
        first_answer = lines[0]
        second_answer = lines[1] if len(lines) == 2 else None

    try:
        msg = api.submit(first_answer, second_answer, year=year, day=day)
        click.echo(msg)
        sys.exit(0)
    except WrongAnswerError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except AlreadyCompletedError as e:
        click.echo(str(e), err=True)
        sys.exit(3)
    except (MissingCookieError, FormNotFoundError, InputNotFoundError, WrongLevelError, AOCError) as e:
        click.echo(str(e), err=True)
        sys.exit(4)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(4)
