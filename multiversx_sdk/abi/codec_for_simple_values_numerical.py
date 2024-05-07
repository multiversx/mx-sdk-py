

import io

from multiversx_sdk.abi.constants import NUM_BYTES_IN_64_BITS
from multiversx_sdk.abi.interface import INumericalValue
from multiversx_sdk.abi.shared import read_bytes_exactly


def encode_nested_unsigned_number(writer: io.BytesIO, value: int, num_bytes: int):
    data = value.to_bytes(num_bytes, byteorder="big", signed=False)
    writer.write(data)


def encode_nested_signed_number(writer: io.BytesIO, value: int, num_bytes: int):
    data = value.to_bytes(num_bytes, byteorder="big", signed=True)
    writer.write(data)


def encode_top_level_unsigned_number(writer: io.BytesIO, value: int):
    if value == 0:
        return

    data = value.to_bytes(NUM_BYTES_IN_64_BITS, byteorder="big", signed=False)
    data = data.lstrip(bytes([0]))
    writer.write(data)


def encode_top_level_signed_number(writer: io.BytesIO, value: int):
    if value == 0:
        return

    length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
    data = value.to_bytes(length, byteorder="big", signed=True)
    writer.write(data)


def decode_nested_unsigned_number(reader: io.BytesIO, value: INumericalValue, num_bytes: int):
    data = read_bytes_exactly(reader, num_bytes)
    value.value = int.from_bytes(data, byteorder="big", signed=False)


def decode_nested_signed_number(reader: io.BytesIO, value: INumericalValue, num_bytes: int):
    data = read_bytes_exactly(reader, num_bytes)
    value.value = int.from_bytes(data, byteorder="big", signed=True)


def decode_top_level_unsigned_number(data: bytes, value: INumericalValue, num_bytes: int):
    value.value = int.from_bytes(data, byteorder="big", signed=False)

    # Do a simple bounds check.
    try:
        value.value.to_bytes(num_bytes, byteorder="big", signed=False)
    except OverflowError:
        raise ValueError(f"decoded value is too large or invalid (does not fit into {num_bytes} bytes): {value.value}")


def decode_top_level_signed_number(data: bytes, value: INumericalValue, num_bytes: int):
    value.value = int.from_bytes(data, byteorder="big", signed=True)

    # Do a simple bounds check.
    try:
        value.value.to_bytes(num_bytes, byteorder="big", signed=True)
    except OverflowError:
        raise ValueError(f"decoded value is too large or invalid (does not fit into {num_bytes} bytes): {value.value}")
