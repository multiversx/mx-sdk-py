from typing import Any, List, Protocol, runtime_checkable

from erdpy_core.constants import ARGUMENTS_SEPARATOR, INTEGER_MAX_NUM_BYTES
from erdpy_core.errors import ErrCannotSerializeArgument


@runtime_checkable
class IArgument(Protocol):
    def serialize(self) -> bytes: ...


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
        return arg.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big").lstrip(bytes([0]))
    if isinstance(arg, bytes):
        return arg
    if isinstance(arg, bytearray):
        return bytes(arg)
    if isinstance(arg, IArgument):
        return arg.serialize()
    raise ErrCannotSerializeArgument(arg)
