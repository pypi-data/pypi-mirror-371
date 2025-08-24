"""
Copyright (c) 2025 by Michal Perzel. All rights reserved.

License: MIT
"""

#: ------------------------------------------------ IMPORTS ------------------------------------------------
import logging
import sys

from logging import Logger
from typing import Union

#: ----------------------------------------------- VARIABLES -----------------------------------------------
__all__ = (
    'common_logger'
)


#: ------------------------------------------------- CLASS -------------------------------------------------


#: ------------------------------------------------ METHODS ------------------------------------------------
def common_logger(name: str | None = None, level: str | int = 'INFO') -> Logger:
    """
    Creates and returns custom instance of Logger object

    Args:
        name (str): Provide name of Logger.
                    Default value is "common_logger"
        level (str|int): Provide one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] or
                         [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    Returns:
        Logger: Logger class instance
    """
    #: Prepare expected values
    expected_int_values = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    expected_string_values = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    #: Check NAME argument is correct type
    if name is None:
        name = 'common_logger'
    elif isinstance(name, int):
        name = str(name)
    elif not isinstance(name, str):
        raise TypeError(f'Provided argument "name" is not str, provided: {type(name)}')

    #: Check LEVEL argument is correct type or value
    if isinstance(level, str):
        level: int | None = expected_string_values.get(level.lower(), None)

        if level is None:
            raise ValueError(
                f'Wrong str value was provided for "level", must be one of {str(list(expected_string_values.keys()))}'
            )

    elif isinstance(level, int) and level not in expected_int_values:
        raise ValueError(
            f'Wrong int value was provided for "level", must be one of {str(expected_int_values)}'
        )

    elif not isinstance(level, (str, int)):
        raise TypeError(f'Provided argument "level" is not str or int, provided: {type(level)}')

    #: Preparing Logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    #: Create a console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    #: Define the log format
    formatter = logging.Formatter('%(asctime)s; %(name)s; %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    #: Add the handler to the logger
    logger.addHandler(handler)

    return logger


#: ------------------------------------------------- BODY --------------------------------------------------
if __name__ == '__main__':
    pass
