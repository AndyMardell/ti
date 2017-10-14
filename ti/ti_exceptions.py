
class TIError(Exception):
    """Errors raised by TI."""


class AlreadyOn(TIError):
    """Already working on that task."""


class NoEditor(TIError):
    """No $EDITOR set."""


class InvalidYAML(TIError):
    """No $EDITOR set."""


class NoTask(TIError):
    """Not working on a task yet."""


class BadTime(TIError):
    """Time string can't be parsed."""


class BadArguments(TIError):
    """The command line arguments passed are not valid."""

