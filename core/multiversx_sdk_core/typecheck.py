"""
Runtime type-checking is not a good idea, generally speaking. 
However, some developers may inadvertently disable static type-checking in their IDEs,
and this can lead to hard-to-debug errors.

The functions in this module are meant to be **internally** used by some components,
in order to guard against misuse of the SDK, which may result in loss of funds.
"""

from typing import Any


def assert_is_integer(value: Any, message: str = ""):
    if not isinstance(value, int):
        message = message or f"Expected integer, got {type(value)}"
        raise ValueError(message)
