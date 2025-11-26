import sys
import click
from typing import Optional

from . import api
from .errors import (
    AOCError,
    MissingCookieError,
    InputNotFoundError,
    FormNotFoundError,
    WrongAnswerError,
    AlreadyCompletedError,
)

@click.group()
def cli():
    """AoC CLI entry point."""
    pass

@cli.command()
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
def fetch(year: Optional[int] = None, day: Optional[int] = None):
    """Fetch puzzle input for a given day."""
    try:
        data = api.fetch(year=year, day=day)
        click.echo(data, nl=False)  # write raw to stdout
    except InputNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except MissingCookieError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error fetching input: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('answer', required=False)
@click.option('--year', type=int, help='Year of the puzzle')
@click.option('--day', type=int, help='Day of the puzzle')
@click.option('--part', type=int, help='Puzzle part')
def submit(answer, year: Optional[int] = None, day: Optional[int] = None, part: Optional[int] = None):
    """Submit an answer to AoC."""
    if answer is None:
        answer = sys.stdin.read().strip()
    if not answer:
        click.echo("No answer provided", err=True)
        sys.exit(2)

    try:
        msg = api.submit(answer, year=year, day=day, part=part)
        click.echo(msg)
        sys.exit(0)
    except WrongAnswerError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except AlreadyCompletedError as e:
        click.echo(str(e), err=True)
        sys.exit(3)
    except (MissingCookieError, FormNotFoundError, InputNotFoundError, AOCError) as e:
        click.echo(str(e), err=True)
        sys.exit(4)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(4)
