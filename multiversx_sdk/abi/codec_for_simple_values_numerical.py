

import io

from multiversx_sdk.abi.constants import NUM_BYTES_IN_64_BITS
from multiversx_sdk.abi.interface import INumericalValue
from multiversx_sdk.abi.shared import read_bytes_exactly


def encode_nested_number(writer: io.BytesIO, value: int, signed: bool, num_bytes: int):
    data = value.to_bytes(num_bytes, byteorder="big", signed=signed)
    writer.write(data)


def encode_top_level_number(writer: io.BytesIO, value: int, signed: bool):
    if value == 0:
        return

    if not signed:
        data = value.to_bytes(NUM_BYTES_IN_64_BITS, byteorder="big", signed=False)
        data = data.lstrip(bytes([0]))
    else:
        length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
        data = value.to_bytes(length, byteorder="big", signed=True)

    writer.write(data)


def decode_nested_number(reader: io.BytesIO, value: INumericalValue, signed: bool, num_bytes: int):
    data = read_bytes_exactly(reader, num_bytes)
    value.value = int.from_bytes(data, byteorder="big", signed=signed)


def decode_top_level_number(data: bytes, value: INumericalValue, signed: bool, num_bytes: int):
    value.value = int.from_bytes(data, byteorder="big", signed=signed)

    # Do a simple bounds check.
    try:
        value.value.to_bytes(num_bytes, byteorder="big", signed=signed)
    except OverflowError:
        raise ValueError(f"decoded value is too small or too large (does not fit into {num_bytes} bytes): {value.value}")
