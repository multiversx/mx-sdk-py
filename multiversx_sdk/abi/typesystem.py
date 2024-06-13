from typing import Any, Sequence

from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.variadic_values import VariadicValues


def is_list_of_bytes(values: Sequence[Any]) -> bool:
    return all(is_bytes(value) for value in values)


def is_bytes(value: Any) -> bool:
    return isinstance(value, bytes)


def is_list_of_typed_values(values: Sequence[Any]) -> bool:
    return all(is_typed_value(value) for value in values)


def is_typed_value(value: Any) -> bool:
    return is_multi_value(value) or is_single_value(value)


def is_single_value(value: Any) -> bool:
    return isinstance(value, ISingleValue)


def is_multi_value(value: Any) -> bool:
    return isinstance(value, MultiValue) or isinstance(value, VariadicValues) or isinstance(value, OptionalValue)
