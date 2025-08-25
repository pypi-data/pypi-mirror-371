import argparse
from typing import Optional

from ._core import LOGGING_LEVELS, LOGGING_WARN


DEFAULT_LOGGING_LEVEL_HELP = "The logging level to use."
DEFAULT_LOGGER_NAME_HELP = "The custom name to use for the logger."


def add_logging_level(parser: argparse.ArgumentParser, short_opt: Optional[str] = "-l",
                      long_opt: Optional[str] = "--logging_level", dest: str = "logging_level",
                      help_str: str = None):
    """
    Adds an option for the logging level to the parser.
    Only one of the two must be supplied: short_opt or long_opt.

    :param parser: the parser to append.
    :type parser: argparse.ArgumentParser
    :param short_opt: the short option flag to use (eg -l), ignored if None
    :type short_opt: str
    :param long_opt: the long option flag to use (eg --logging_level), ignored if None
    :type long_opt: str
    :param dest: the name to use in the parsed namespace
    :type dest: str
    :param help_str: the help string to use
    :type help_str: str
    """
    if help_str is None:
        help_str = DEFAULT_LOGGING_LEVEL_HELP
    if (short_opt is None) and (long_opt is None):
        raise Exception("Either short or long option must be supplied at least!")
    elif (short_opt is not None) and (long_opt is not None):
        parser.add_argument(short_opt, long_opt, dest=dest, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)
    elif short_opt is not None:
        parser.add_argument(short_opt, dest=dest, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)
    else:
        parser.add_argument(long_opt, dest=dest, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)


def add_logger_name(parser: argparse.ArgumentParser, short_opt: str = "-N", long_opt: str = "--logger_name",
                    dest: str = "logger_name", default_name: str = None, help_str: str = None):
    """
    Adds an option for the logger name to the parser.
    Only one of the two must be supplied: short_opt or long_opt.

    :param parser: the parser to append.
    :type parser: argparse.ArgumentParser
    :param short_opt: the short option flag to use (eg -N), ignored if None
    :type short_opt: str
    :param long_opt: the long option flag to use (eg --logger_name), ignored if None
    :type long_opt: str
    :param dest: the name to use in the parsed namespace
    :type dest: str
    :param default_name: the default name for the logger
    :type default_name: str
    :param help_str: the help string to use
    :type help_str: str
    """
    if help_str is None:
        help_str = DEFAULT_LOGGER_NAME_HELP
    if (short_opt is None) and (long_opt is None):
        raise Exception("Either short or long option must be supplied at least!")
    elif (short_opt is not None) and (long_opt is not None):
        parser.add_argument(short_opt, long_opt, type=str, dest=dest, default=default_name, help=help_str, required=False)
    elif short_opt is not None:
        parser.add_argument(short_opt, type=str, dest=dest, default=default_name, help=help_str, required=False)
    else:
        parser.add_argument(long_opt, type=str, dest=dest, default=default_name, help=help_str, required=False)
