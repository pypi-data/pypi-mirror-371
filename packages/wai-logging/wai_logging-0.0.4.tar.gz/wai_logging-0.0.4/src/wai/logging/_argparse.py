import argparse
from typing import Optional

from ._core import LOGGING_LEVELS, LOGGING_WARN


def add_logging_level(parser: argparse.ArgumentParser, short_opt: Optional[str] = "-l",
                      long_opt: Optional[str] = "--logging_level", help_str: str = None):
    """
    Adds an option for the logging level to the parser.

    :param parser: the parser to append.
    :type parser: argparse.ArgumentParser
    :param short_opt: the short option flag to use (eg -l), ignored if None
    :type short_opt: str
    :param long_opt: the long option flag to use (eg --logging_level), ignored if None
    :type long_opt: str
    :param help_str: the help string to use
    :type help_str: str
    """
    if help_str is None:
        help_str = "The logging level to use."
    if (short_opt is None) and (long_opt is None):
        raise Exception("At least either short or long option must be supplied!")
    elif short_opt is not None:
        parser.add_argument(short_opt, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)
    elif long_opt is not None:
        parser.add_argument(long_opt, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)
    else:
        parser.add_argument(short_opt, long_opt, choices=LOGGING_LEVELS, default=LOGGING_WARN, help=help_str)


def add_logger_name(parser: argparse.ArgumentParser, short_opt: str = "-N", long_opt: str = "--logger_name",
                    help_str: str = None):
    """
    Adds an option for the logger name to the parser.

    :param parser: the parser to append.
    :type parser: argparse.ArgumentParser
    :param short_opt: the short option flag to use (eg -N)
    :type short_opt: str
    :param long_opt: the long option flag to use (eg --logger_name)
    :type long_opt: str
    :param help_str: the help string to use
    :type help_str: str
    """
    if help_str is None:
        help_str = "The custom name to use for the logger"
    parser.add_argument(short_opt, long_opt, type=str, default=None, help=help_str, required=False)
