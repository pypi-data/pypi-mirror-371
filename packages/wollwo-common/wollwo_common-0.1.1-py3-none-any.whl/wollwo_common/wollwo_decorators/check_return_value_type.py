"""
Copyright (c) 2025 by Michal Perzel. All rights reserved.

License: MIT
"""

#: ------------------------------------------------ IMPORTS ------------------------------------------------
from functools import wraps
from inspect import isfunction
from typing import Any, Type, Optional

#: ----------------------------------------------- VARIABLES -----------------------------------------------
__all__ = (
    'CheckReturnValueType'
)


#: ------------------------------------------------- CLASS -------------------------------------------------
class CheckReturnValueType:
    """
    Functions as decorator and context manager for checking if
    return value of wrapped function return value of expected type

    Raises:
        TypeError

    """
    def __init__(
            self,
            expected_type: Optional[Type[Any]],
            /, *,
            use_annotation: bool = False
            # raise_exception: bool = True
    ):
        """

        Parameters:
            expected_type (Type[Any]):
                what type must be returned value of wrapped method
            use_annotation (bool):
                use annotation as expected_type,
                defaults to expected_type if annotation is not provided
            # raise_exception (bool):
            #     if True, raise TypeError exception if returned value is of wrong type

        """
        self.expected_type = expected_type
        self.use_annotation = use_annotation
        # self.raise_exception = raise_exception

    def __enter__(self):
        """You can perform setup actions here if needed"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """You can perform cleanup actions here if needed"""

        #: Check for excepted exception
        if exc_type is not None:
            if (isinstance(exc_type(), TypeError)
                    and exc_type.__name__ == TypeError.__name__):
                return False
            pass
        pass

    def check(self, func, *args, **kwargs):
        """
        run wrapped function, check if return value of correct type
        raise TypeError exception if not (raise_exception=True)

        Returns:
            func
        """
        if not isfunction(func):
            raise TypeError(f'Expected "func" to be callable function, got "{type(func).__name__}"')

        #: check if __annotation__ are provided and self.use_annotation=True
        expected_func_type = self.expected_type
        if self.use_annotation:
            expected_func_type = func.__annotations__.get('return', self.expected_type)

        #: run wrapped function
        result = func(*args, **kwargs)

        #: check return value
        if expected_func_type is not None and not isinstance(result, expected_func_type):
            raise TypeError(f'Expected return type "{expected_func_type}", got "{type(result)}"')
        elif expected_func_type is None and expected_func_type is not result:
            raise TypeError(f'Expected return type "NoneType", got "{type(result)}"')

        return result

    def __call__(self, func):
        """can be used as decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return self.check(func, *args, **kwargs)
        return wrapper



#: ------------------------------------------------ METHODS ------------------------------------------------


#: ------------------------------------------------- BODY --------------------------------------------------
if __name__ == '__main__':
    pass
