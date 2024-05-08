

import io

from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.abi.values_single import BytesValue


class CodecForBytes:
    def encode_nested(self, writer: io.BytesIO, value: BytesValue):
        encode_length(writer, len(value.value))
        writer.write(value.value)

    def encode_top_level(self, writer: io.BytesIO, value: BytesValue):
        writer.write(value.value)

    def decode_nested(self, reader: io.BytesIO, value: BytesValue):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        value.value = data

    def decode_top_level(self, data: bytes, value: BytesValue):
        value.value = data
