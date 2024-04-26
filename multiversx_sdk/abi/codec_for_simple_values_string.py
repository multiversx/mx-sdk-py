

import io

from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.abi.values_single import StringValue


def encode_nested_string(writer: io.BytesIO, value: StringValue):
    encode_length(writer, len(value.value))
    writer.write(value.value.encode("utf-8"))


def encode_top_level_string(writer: io.BytesIO, value: StringValue):
    writer.write(value.value.encode("utf-8"))


def decode_nested_string(reader: io.BytesIO, value: StringValue):
    length = decode_length(reader)
    data = read_bytes_exactly(reader, length)
    value.value = data.decode("utf-8")


def decode_top_level_string(data: bytes, value: StringValue):
    value.value = data.decode("utf-8")
