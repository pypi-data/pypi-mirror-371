"""
Copyright (c) 2025 by Michal Perzel. All rights reserved.

License: MIT
"""

#: ------------------------------------------------ IMPORTS ------------------------------------------------
import logging

from dataclasses import dataclass, field, fields, asdict, MISSING
from typing import Optional

from .common_logger import common_logger

#: ----------------------------------------------- VARIABLES -----------------------------------------------
__all__ = (
    'CommonLogLineBase'
)


#: ------------------------------------------------- CLASS -------------------------------------------------
@dataclass
class CommonLogLineBase:
    """Reusable wollwo-common class handling logging"""
    logger_name: str
    logger_level: str = field(default='INFO')
    logger_text_format: str = field(default='%(asctime)s; %(name)s; %(message)s')
    logger_date_format: str = field(default='%Y-%m-%d %H:%M:%S')

    #: Not visible
    __logger: Optional[logging.Logger] = field(default=None, init=False, repr=False)
    __allowed_levels: dict = field(
        default_factory=lambda: {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        },
        init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Post init tasks"""

        self.init_logger()

        return

    def __setattr__(self, name, value):
        """Custom attribute setter"""

        attributes = {attr.name: attr.type for attr in fields(self)}

        #: expect general STR for all attributes
        if name in attributes.keys() and not isinstance(value, attributes[name]):
            raise TypeError(f"Expected '{name}' to be of type '{attributes[name]}', got {type(value).__name__}")

        #: Specific values
        if name == "level":
            value = value.upper()
            if value not in self.__allowed_levels.keys():
                raise ValueError(f"Expected '{name}' to be in {list(self.__allowed_levels.keys())}")

        super().__setattr__(name, value)

    def init_logger(self) -> None:
        """initialize logger"""
        self.__logger = common_logger(name=None, level='INFO')

    @staticmethod
    def __prepare_text(text: str, qualname: str | None) -> str:
        """
        add additional qualname string to text

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__
        Returns:
            str
        """

        if qualname is not None and not isinstance(qualname, str):
            raise TypeError(f"Expected 'qualname' to be of type 'str', got {type(qualname).__name__}")

        if not isinstance(text, str):
            raise TypeError(f"Expected 'text' to be of type 'str', got {type(text).__name__}")

        return f'{text}' if qualname is None else f'{qualname}: {text}'

    def debug(self, text: str, qualname: str) -> None:
        """
        log provided text with logging.Logger as debug line

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__

        Returns:
            None
        """

        text = self.__prepare_text(text, qualname)
        self.__logger.debug(text)

        return

    def info(self, text: str, qualname: str | None = None) -> None:
        """
        log provided text with logging.Logger as info line

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__
                            default = None

        Returns:
            None
        """
        text = self.__prepare_text(text, qualname)
        self.__logger.info(text)

        return

    def warning(self, text: str, qualname: str) -> None:
        """
        log provided text with logging.Logger as warning line

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__
                            default = None

        Returns:
            None
        """

        text = self.__prepare_text(text, qualname)
        self.__logger.warning(text)

        return

    def error(self, text: str, qualname: str) -> None:
        """
        log provided text with logging.Logger as error line

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__
                            default = None

        Returns:
            None
        """
        text = self.__prepare_text(text, qualname)
        self.__logger.error(text)

        return

    def critical(self, text: str, qualname: str) -> None:
        """
        log provided text with logging.Logger as critical line

        Attr:
            text (str): string to log
            qualname (str): string to add to text, qualname as in *.__qualname__
                            default = None

        Returns:
            None
        """
        text = self.__prepare_text(text, qualname)
        self.__logger.critical(text)

        return


#: ------------------------------------------------ METHODS ------------------------------------------------


#: ------------------------------------------------- BODY --------------------------------------------------
if __name__ == '__main__':
    pass
