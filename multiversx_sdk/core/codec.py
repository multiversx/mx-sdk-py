
from multiversx_sdk.core.constants import INTEGER_MAX_NUM_BYTES


def encode_unsigned_number(arg: int) -> bytes:
    return arg.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big", signed=False).lstrip(bytes([0]))


def encode_signed_number(arg: int) -> bytes:
    if arg == 0:
        return b''
    length = ((arg + (arg < 0)).bit_length() + 7 + 1) // 8
    return arg.to_bytes(length, byteorder="big", signed=True)


def decode_unsigned_number(arg: bytes) -> int:
    return int.from_bytes(arg, byteorder="big", signed=False)


def decode_signed_number(arg: bytes) -> int:
    return int.from_bytes(arg, byteorder="big", signed=True)
