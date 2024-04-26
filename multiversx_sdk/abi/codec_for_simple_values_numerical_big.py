
import io

from multiversx_sdk.abi.interface import INumericalValue
from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.core.constants import INTEGER_MAX_NUM_BYTES


def encode_nested_big_number(writer: io.BytesIO, value: int, signed: bool):
    data = big_number_to_bytes(value, signed)
    encode_length(writer, len(data))
    writer.write(data)


def encode_top_level_big_number(writer: io.BytesIO, value: int, signed: bool):
    data = big_number_to_bytes(value, signed)
    writer.write(data)


def decode_nested_big_number(reader: io.BytesIO, value: INumericalValue, signed: bool):
    length = decode_length(reader)
    data = read_bytes_exactly(reader, length)
    value.value = big_number_from_bytes(data, signed)


def decode_top_level_big_number(data: bytes, value: INumericalValue, signed: bool):
    value.value = big_number_from_bytes(data, signed)


def big_number_to_bytes(value: int, signed: bool) -> bytes:
    if value == 0:
        return b''

    if not signed:
        data = value.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big", signed=False)
        data = data.lstrip(bytes([0]))
    else:
        length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
        data = value.to_bytes(length, byteorder="big", signed=True)

    return data


def big_number_from_bytes(data: bytes, signed: bool) -> int:
    return int.from_bytes(data, byteorder="big", signed=signed)
