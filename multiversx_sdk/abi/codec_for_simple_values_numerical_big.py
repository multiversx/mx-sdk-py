
import io

from multiversx_sdk.abi.interface import INumericalValue
from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.core.constants import INTEGER_MAX_NUM_BYTES


def encode_nested_unsigned_big_number(writer: io.BytesIO, value: int):
    data = _unsigned_big_number_to_bytes(value)
    encode_length(writer, len(data))
    writer.write(data)


def encode_nested_signed_big_number(writer: io.BytesIO, value: int):
    data = _signed_big_number_to_bytes(value)
    encode_length(writer, len(data))
    writer.write(data)


def encode_top_level_unsigned_big_number(writer: io.BytesIO, value: int):
    data = _unsigned_big_number_to_bytes(value)
    writer.write(data)


def encode_top_level_signed_big_number(writer: io.BytesIO, value: int):
    data = _signed_big_number_to_bytes(value)
    writer.write(data)


def decode_nested_unsigned_big_number(reader: io.BytesIO, value: INumericalValue):
    length = decode_length(reader)
    data = read_bytes_exactly(reader, length)
    value.value = _unsigned_big_number_from_bytes(data)


def decode_nested_signed_big_number(reader: io.BytesIO, value: INumericalValue):
    length = decode_length(reader)
    data = read_bytes_exactly(reader, length)
    value.value = _signed_big_number_from_bytes(data)


def decode_top_level_unsigned_big_number(data: bytes, value: INumericalValue):
    value.value = _unsigned_big_number_from_bytes(data)


def decode_top_level_signed_big_number(data: bytes, value: INumericalValue):
    value.value = _signed_big_number_from_bytes(data)


def _unsigned_big_number_to_bytes(value: int) -> bytes:
    if value == 0:
        return b''

    data = value.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big", signed=False)
    data = data.lstrip(bytes([0]))
    return data


def _signed_big_number_to_bytes(value: int) -> bytes:
    if value == 0:
        return b''

    length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
    data = value.to_bytes(length, byteorder="big", signed=True)
    return data


def _unsigned_big_number_from_bytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big", signed=False)


def _signed_big_number_from_bytes(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big", signed=True)
