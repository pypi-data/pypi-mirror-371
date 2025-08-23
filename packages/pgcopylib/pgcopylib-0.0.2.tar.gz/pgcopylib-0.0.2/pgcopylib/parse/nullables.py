from types import (
    FunctionType,
    NoneType,
)
from typing import (
    Any,
    Optional,
)


def if_nullable(to_dtype: FunctionType):
    """Decorator for solve None value."""

    def wrapper(binary_data: Optional[bytes]) -> Optional[Any]:

        if isinstance(binary_data, NoneType):
            return

        return to_dtype(binary_data)

    return wrapper
