from typing import Any, List, Protocol, Sequence, runtime_checkable

from multiversx_sdk.core.codec import (encode_signed_number,
                                       encode_unsigned_number)
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.core.errors import ErrCannotSerializeArgument


@runtime_checkable
class IArgument(Protocol):
    def serialize(self) -> bytes:
        ...


def args_to_string(args: Sequence[Any]) -> str:
    strings = args_to_strings(args)
    return ARGS_SEPARATOR.join(strings)


def args_to_strings(args: Sequence[Any]) -> List[str]:
    buffers = args_to_buffers(args)
    return [buffer.hex() for buffer in buffers]


def args_to_buffers(args: Sequence[Any]) -> List[bytes]:
    return [arg_to_buffer(arg) for arg in args]


def arg_to_string(arg: Any) -> str:
    buffer = arg_to_buffer(arg)
    return buffer.hex()


def arg_to_buffer(arg: Any) -> bytes:
    if isinstance(arg, str):
        return arg.encode("utf-8")
    if isinstance(arg, int):
        if arg < 0:
            return encode_signed_number(arg)
        return encode_unsigned_number(arg)
    if isinstance(arg, bytes):
        return arg
    if isinstance(arg, bytearray):
        return bytes(arg)
    if isinstance(arg, IArgument):
        return arg.serialize()
    raise ErrCannotSerializeArgument(arg)
