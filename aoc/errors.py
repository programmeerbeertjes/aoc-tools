class AOCError(Exception):
    """Base class for AoC errors."""


class UnknownDateError(AOCError):
    pass


class MissingCookieError(AOCError):
    pass


class InputNotFoundError(AOCError):
    pass


class FormNotFoundError(AOCError):
    pass


class WrongLevelError(AOCError):
    pass


class WrongAnswerError(AOCError):
    """Raised when the server reports a wrong answer."""


class AlreadyCompletedError(AOCError):
    """Raised when the puzzle part is already solved / cannot submit."""
