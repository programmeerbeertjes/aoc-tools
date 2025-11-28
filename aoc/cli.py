import sys
from datetime import date as _date
from typing import Optional, Tuple

import click

from . import api, config
from .errors import (
    AOCError,
    MissingCookieError,
    InputNotFoundError,
    FormNotFoundError,
    WrongLevelError,
    WrongAnswerError,
    AlreadyCompletedError,
)


# ------------------------------
# Helpers
# ------------------------------
def _validate_date_opts(year: Optional[int], day: Optional[int], date: Optional[Tuple[int, int]]):
    """
    Validate combination of --date vs --year/--day.
    If date is provided, year/day must not be provided.
    Returns (year, day) where either item may be None (and will be resolved in API).
    """
    if date is not None:
        # date is a (year, day) tuple produced by DATE_TYPE (or None)
        if year is not None or day is not None:
            click.echo("Cannot use --date with --year or --day", err=True)
            sys.exit(2)
        return date  # explicit tuple (year, day)
    return year, day


class DateOption(click.ParamType):
    """
    Parses --date values of the form:
        "2023/8"
        "2024/03"
        "today"
    Returns a tuple (year, day)
    """

    name = "date"

    def convert(self, value, param, ctx):
        if value == "today":
            today = _date.today()
            return today.year, today.day

        try:
            year_str, day_str = value.split("/")
            return int(year_str), int(day_str)
        except Exception:
            self.fail(
                "Invalid date format. Expected 'YYYY/D', 'YYYY/DD', or 'today'",
                param,
                ctx,
            )

DATE_TYPE = DateOption()

# Options for CLI arguments
_year_option = click.option("--year", "-y", type=int, help="Year of the puzzle")
_day_option = click.option("--day", "-d", type=int, help="Day of the puzzle")
_idx_option = click.option("--idx", "-i", type=int, default=None, help="0-based index of code block")
_sep_option = click.option("--sep", "-s", type=str, default="\n", help="Separator for multiple blocks")
_date_option = click.option("--date", "-D", type=DATE_TYPE, default=None,
                            help="Combined date as 'YYYY/D' or 'YYYY/DD' or 'today'")
_cookie_option = click.option("--cookie", "-c", type=str, default=None,
                              help="Cookie for personalized puzzle input and submission")

# ------------------------------
# Main entry point
# ------------------------------
@click.group()
def cli():
    """AoC CLI entry point."""
    pass

# ------------------------------
# Fetching commands
# ------------------------------
@cli.group()
def fetch():
    """Fetch puzzle input, code, or example blocks."""
    pass


@fetch.command("input")
@_year_option
@_day_option
@_date_option
@_cookie_option
def fetch_input(year: Optional[int] = None, day: Optional[int] = None, date: Optional[Tuple[int, int]] = None, cookie: Optional[str] = None):
    """Fetch puzzle input for a given day (plain text)."""
    year, day = _validate_date_opts(year, day, date)
    try:
        data = api.fetch_input(year=year, day=day, cookie=cookie)
        # print raw input without extra newline
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
@_year_option
@_day_option
@_date_option
@_idx_option
@_sep_option
def fetch_code(year: Optional[int] = None, day: Optional[int] = None, date: Optional[Tuple[int, int]] = None,
               idx: Optional[int] = None, sep: str = "\n"):
    """Fetch <pre><code> blocks from the problem page."""
    year, day = _validate_date_opts(year, day, date)
    try:
        data = api.fetch_code(year=year, day=day, idx=idx, sep=sep)
        click.echo(data)
    except Exception as e:
        click.echo(f"Error fetching code blocks: {e}", err=True)
        sys.exit(1)


@fetch.command("example")
@_year_option
@_day_option
@_date_option
@_idx_option
@_sep_option
def fetch_example(year: Optional[int] = None, day: Optional[int] = None, date: Optional[Tuple[int, int]] = None,
                  idx: Optional[int] = None, sep: str = "\n"):
    """Fetch example <pre><code> blocks preceded by 'for example:' paragraph."""
    year, day = _validate_date_opts(year, day, date)
    try:
        data = api.fetch_example(year=year, day=day, idx=idx, sep=sep)
        click.echo(data)
    except Exception as e:
        click.echo(f"Error fetching example blocks: {e}", err=True)
        sys.exit(1)


# ------------------------------
# Submit puzzle answers
# ------------------------------
@cli.command()
@click.argument("first_answer", required=False)
@click.argument("second_answer", required=False)
@_year_option
@_day_option
@_date_option
@_cookie_option
def submit(first_answer, second_answer, year: Optional[int] = None, day: Optional[int] = None,
           date: Optional[Tuple[int, int]] = None, cookie: Optional[str] = None):
    """Submit one or two answers to AoC."""

    year, day = _validate_date_opts(year, day, date)

    # Read stdin (strip blank lines)
    stdin_lines = [line.strip() for line in sys.stdin if line.strip()]

    # No answers provided
    if first_answer is None and not stdin_lines:
        click.echo("No answers provided", err=True)
        sys.exit(2)

    # Cannot mix CLI args with stdin input
    if first_answer is not None and stdin_lines:
        click.echo("Cannot mix command-line answers and stdin input", err=True)
        sys.exit(2)

    # If reading from stdin, ensure <= 2 non-blank lines
    if stdin_lines and len(stdin_lines) > 2:
        click.echo("Too many answers; expected 1 or 2", err=True)
        sys.exit(2)

    # Populate answers from stdin if necessary
    if first_answer is None:
        first_answer = stdin_lines[0]
        second_answer = stdin_lines[1] if len(stdin_lines) == 2 else None

    try:
        msg = api.submit(first_answer, second_answer, year=year, day=day, cookie=cookie)
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


# ------------------------------
# Configuration commands
# ------------------------------
@cli.group("config")
def config_cmd():
    """Manage AoC local configuration"""
    pass


@config_cmd.group("set")
def config_set():
    """Set configuration values"""
    pass


@config_set.command("year")
@click.argument("value", type=int)
def set_year(value: int):
    config.year = value
    click.echo(f"year set to {value}")


@config_set.command("day")
@click.argument("value", type=int)
def set_day(value: int):
    config.day = value
    click.echo(f"day set to {value}")


@config_set.command("cookie")
@click.argument("value", type=str)
def set_cookie(value: str):
    config.cookie = value
    click.echo("cookie set")


@config_set.command("date")
@click.argument("value", type=DATE_TYPE)
def set_date(value: Tuple[int, int]):
    """
    Set a combined date. DATE_TYPE accepts 'YYYY/D', 'YYYY/DD', or 'today'.
    DATE_TYPE returns an explicit (year, day) tuple; we store that tuple.
    """
    year, day = value
    config.date = (year, day)
    click.echo(f"date set to {year}/{day}")


@config_cmd.group("unset")
def config_unset():
    """Unset configuration values"""
    pass


@config_unset.command("year")
def unset_year():
    try:
        del config.year
        click.echo("year unset")
    except Exception:
        click.echo("year was not set", err=True)
        sys.exit(1)


@config_unset.command("day")
def unset_day():
    try:
        del config.day
        click.echo("day unset")
    except Exception:
        click.echo("day was not set", err=True)
        sys.exit(1)


@config_unset.command("cookie")
def unset_cookie():
    try:
        del config.cookie
        click.echo("cookie unset")
    except Exception:
        click.echo("cookie was not set", err=True)
        sys.exit(1)


@config_cmd.group("get")
def config_get():
    """Get configuration values"""
    pass


@config_get.command("year")
def get_year():
    click.echo(config.year)


@config_get.command("day")
def get_day():
    click.echo(config.day)


@config_get.command("cookie")
def get_cookie():
    click.echo(config.cookie)


@config_get.command("date")
def get_date():
    # Return the explicit values stored in config (not env/resolved)
    y, d = config.date
    if y is None and d is None:
        click.echo("")  # consistent with previous behavior of printing nothing
    else:
        click.echo(f"{y}/{d}")


@config_cmd.command("list")
def list_cmd():
    """List all stored configuration values"""
    data = config.list()
    for k, v in data.items():
        click.echo(f"{k} = {v}")


@config_cmd.command("clear")
def clear_cmd():
    config.clear()
    click.echo("configuration cleared")
