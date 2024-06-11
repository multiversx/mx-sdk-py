import io
from typing import Any, Optional

from multiversx_sdk.abi.constants import (OPTION_MARKER_FOR_ABSENT_VALUE,
                                          OPTION_MARKER_FOR_PRESENT_VALUE)
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.shared import read_bytes_exactly


class OptionValue:
    def __init__(self, value: Optional[ISingleValue] = None) -> None:
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        if self.value is None:
            writer.write(bytes([OPTION_MARKER_FOR_ABSENT_VALUE]))
            return

        writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
        self.value.encode_nested(writer)

    def encode_top_level(self, writer: io.BytesIO):
        if self.value is None:
            return

        writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
        self.value.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        if self.value is None:
            raise ValueError("placeholder value of option should be set before decoding")

        data = read_bytes_exactly(reader, 1)
        first_byte = data[0]

        if first_byte == OPTION_MARKER_FOR_ABSENT_VALUE:
            self.value = None
            return

        if first_byte == OPTION_MARKER_FOR_PRESENT_VALUE:
            self.value.decode_nested(reader)
            return

        raise ValueError(f"invalid first byte for nested encoded option: {first_byte}")

    def decode_top_level(self, data: bytes):
        if self.value is None:
            raise ValueError("placeholder value of option should be set before decoding")

        if len(data) == 0:
            self.value = None
            return

        first_byte = data[0]
        data_after_first_byte = data[1:]

        if first_byte != OPTION_MARKER_FOR_PRESENT_VALUE:
            raise ValueError(f"invalid first byte for top-level encoded option: {first_byte}")

        reader = io.BytesIO(data_after_first_byte)
        self.value.decode_nested(reader)

