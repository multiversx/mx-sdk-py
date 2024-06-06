import io
from typing import Any

from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)


class StringValue:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        encode_length(writer, len(self.value))
        writer.write(self.value.encode("utf-8"))

    def encode_top_level(self, writer: io.BytesIO):
        writer.write(self.value.encode("utf-8"))

    def decode_nested(self, reader: io.BytesIO):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        self.value = data.decode("utf-8")

    def decode_top_level(self, data: bytes):
        self.value = data.decode("utf-8")

