

import io

from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.abi.values_single import StringValue


class CodecForString:
    def encode_nested(self, writer: io.BytesIO, value: StringValue):
        encode_length(writer, len(value.value))
        writer.write(value.value.encode("utf-8"))

    def encode_top_level(self, writer: io.BytesIO, value: StringValue):
        writer.write(value.value.encode("utf-8"))

    def decode_nested(self, reader: io.BytesIO, value: StringValue):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        value.value = data.decode("utf-8")

    def decode_top_level(self, data: bytes, value: StringValue):
        value.value = data.decode("utf-8")
