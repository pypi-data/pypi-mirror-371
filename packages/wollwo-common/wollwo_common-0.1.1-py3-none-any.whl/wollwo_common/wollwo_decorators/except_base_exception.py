"""
Copyright (c) 2025 by Michal Perzel. All rights reserved.

License: MIT
"""

#: ------------------------------------------------ IMPORTS ------------------------------------------------
import sys
import traceback

from dataclasses import dataclass, field, fields
from functools import wraps
from logging import Logger
from typing import Optional, Union, Callable

#: ----------------------------------------------- VARIABLES -----------------------------------------------
__all__ = (
    'ExceptBaseException'
)


#: ------------------------------------------------- CLASS -------------------------------------------------
@dataclass
class ExceptBaseException:
    """
    Context manager / Decorator for excepting BaseException.
    It will pass through any other type of exception

    Handles "BaseException" Exception:
      - exit on exception
      - silence exception
      - print traceback on exception

    Parameters:
        qualname (str):
        custom_logger (Logger): Default None
            logger which should be used to log/print messages
            (from logging library)
        execute_on_exc (callable): Default None
            if provided callable, it will be executed after logger and before trace
        execute_on_exc_params (Tuple[List[Any], Dict[Any, Any]]): Default None
            if provided it will be used as args, kwargs for execute_on_exc callable
        exit_on_exc (int): Default None
            provide exit code, from 0-255
            If value is provided, exception will exit with provided code
            if not None, silence_exc will not be executed
        print_trace (bool): Default True
            will print traceback before raisin/exiting/silencing exception
            print trace just before exit or silence
        silence_exc (bool): Default False
            silence exception, if not exited first
            Your code will be stopped at place where exception will be raised naturally
            if you have more code to be executed think about passing exception
        pass_exc (bool): Default False
            exception will be passed (not raised, not silenced)
        exception_responses (list)
            each excepted exception will be logged to list of dicts

    Exceptions:
        TypeError: raised by:
            - __setattr__() on provided wrong attribute Type
    """

    qualname: str = field(default_factory=lambda: ExceptBaseException.__init__.__qualname__)
    custom_logger: Optional[Logger] = field(default=None)
    execute_on_exc: Optional[Callable] = field(default=None)
    execute_on_exc_params: Optional[tuple] = field(default=None)
    exit_on_exc: Optional[int] = field(default=None)
    print_trace: bool = field(default=True)
    silence_exc: bool = field(default=False)
    pass_exc: bool = field(default=False)

    #: Changeable instance values, not meant for init
    exception_responses: list = field(
        default_factory=list,
        init=False
    )
    level: str = field(default='error', init=False)

    #: internal attributes not meant to be changed
    _expected_exception: BaseException = field(default=BaseException, init=False, repr=False)
    __rep: int = field(default=30, init=False, repr=False)

    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Exception handling and other cleaning tasks"""

        #: Check for excepted exception
        if exc_type is not None:
            if (isinstance(exc_type(), BaseException) and
                    exc_type.__name__ == self._expected_exception.__name__
            ):
                #: prepare silence
                silence = self.silence_exc if isinstance(self.silence_exc, bool) else False

                #: prepare response
                text = f'{exc_type.__name__}: {exc_value}'
                self.exception_responses.append(
                    {
                        'exception': self._expected_exception.__name__,
                        'response': text
                    }
                )

                #: logger
                self.__internal_logger(self.level, text)

                if self.execute_on_exc is not None:
                    self.__internal_logger(
                        'debug',
                        f'{exc_type.__name__}: Executing custom method'
                    )
                    args: list = []
                    kwargs: dict = {}
                    for item in self.execute_on_exc_params:
                        if isinstance(item, list):
                            args.extend(item)
                        elif isinstance(item, dict):
                            kwargs.update(item)
                        elif isinstance(item, Union[str, int, callable]):
                            args.append(item)
                        else:
                            raise TypeError(f'{self.__class__.__qualname__}(): Unexpected type in execute_on_exc_params')

                    self.execute_on_exc(*args, **kwargs)

                #: Traceback
                if self.print_trace:
                    self.__internal_logger(
                        'debug',
                        f'{exc_type.__name__}: Printing trace of "{exc_type.__name__}"'
                    )
                    self.__print_traceback(exc_type, exc_value, exc_tb)

                #: Exit
                if self.exit_on_exc is not None:
                    self.__internal_logger(
                        'error',
                        f'{exc_type.__name__}: Exiting with {self.exit_on_exc}'
                    )
                    sys.exit(self.exit_on_exc)

                #: silence or raise if not passed
                if not self.pass_exc:
                    if silence:
                        self.__internal_logger(
                            'debug',
                            f'{exc_type.__name__}: Silencing excepted exception "{exc_type.__name__}"'
                        )
                    return silence

            self.__internal_logger(
                'debug',
                f'Passing on raised exception: "{exc_type.__name__}: {exc_value}"'
            )
        pass

    def __call__(self, func):
        """Decorator"""

        self.qualname = func.__qualname__

        @wraps(func)
        def wrapper(*args, **kwargs):
            # with self as context_self:
            #     return func(context_self, *args, **kwargs)
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __setattr__(self, name, value):
        """
        setting and checking attributes based on expected annotations

        Be aware that you must specify exact types, "typing" types can be used
        """

        attributes = {attr.name: attr.type for attr in fields(self)}

        #: Check provided types for all attributes, raise TypeError if there is no match
        if name in attributes.keys() and not isinstance(value, attributes[name]):
            raise TypeError(f'Expected "{name}" to be of type "{attributes[name]}", got {type(value).__name__}')

        if hasattr(super(), '__setattr__'):
            super().__setattr__(name, value)

    def __internal_logger(self, level: Optional[str], text: Optional[str], /) -> None:
        """
        internal logging mechanism for class

        Parameters:
            level (str):
                one of ['debug', 'info', 'warning', 'error', 'critical']
            text (str):
                printed
        """

        expected_values = ['debug', 'info', 'warning', 'error', 'critical']

        if self.custom_logger is None:
            level = level.upper() if level.lower() in expected_values else 'ERROR'

            text = str(text)

            print(f'{level}: {self.qualname} : {text}')

        else:
            match level.lower():
                case 'debug':
                    self.custom_logger.debug(f'{text}')
                case 'info':
                    self.custom_logger.info(f'{text}')
                case 'warning':
                    self.custom_logger.warning(f'{text}')
                case 'error':
                    self.custom_logger.error(f'{text}')
                case 'critical':
                    self.custom_logger.critical(f'{text}')
                case _:
                    raise ValueError(f'Value of "level" must be one of [{", ".join(expected_values)}]')

        return

    def __print_traceback(self, exc_type, exc_value, traceback_obj):
        """
        print captured traceback
        """
        print(f'{"=" * self.__rep} Traceback START {"=" * self.__rep}')
        traceback.print_exception(exc_type, exc_value, traceback_obj)
        print(f'{"=" * (self.__rep + 1)} Traceback END {"=" * (self.__rep + 1)}')


#: ------------------------------------------------ METHODS ------------------------------------------------


#: ------------------------------------------------- BODY --------------------------------------------------
if __name__ == '__main__':
    pass
