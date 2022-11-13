from typing import Any, List

from erdpy_core.constants import ARGUMENTS_SEPARATOR
from erdpy_core.errors import ErrCannotSerializeArgument


def args_to_string(args: List[Any]) -> str:
    strings = args_to_strings(args)
    return ARGUMENTS_SEPARATOR.join(strings)


def args_to_strings(args: List[Any]) -> List[str]:
    buffers = args_to_buffers(args)
    return [buffer.hex() for buffer in buffers]


def args_to_buffers(args: List[Any]) -> List[bytes]:
    return [arg_to_buffer(arg) for arg in args]


def arg_to_buffer(arg: Any) -> bytes:
    if isinstance(arg, str):
        return arg.encode("utf-8")
    if isinstance(arg, int):
        return arg.to_bytes(32, byteorder="big").lstrip(bytes([0]))
    if isinstance(arg, bytes):
        return arg
    raise ErrCannotSerializeArgument(arg)
