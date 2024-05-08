import io

from multiversx_sdk.abi.constants import (OPTION_MARKER_FOR_ABSENT_VALUE,
                                          OPTION_MARKER_FOR_PRESENT_VALUE)
from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.values_single import OptionValue


class CodecForOption:
    def __init__(self, general_codec: ICodec) -> None:
        self.general_codec = general_codec

    def encode_nested(self, writer: io.BytesIO, value: OptionValue):
        if value.value is None:
            writer.write(bytes([OPTION_MARKER_FOR_ABSENT_VALUE]))
            return

        writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
        self.general_codec.do_encode_nested(writer, value.value)

    def encode_top_level(self, writer: io.BytesIO, value: OptionValue):
        if value.value is None:
            return

        writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
        self.general_codec.do_encode_nested(writer, value.value)

    def decode_nested(self, reader: io.BytesIO, value: OptionValue):
        data = read_bytes_exactly(reader, 1)
        first_byte = data[0]

        if first_byte == OPTION_MARKER_FOR_ABSENT_VALUE:
            value.value = None
            return

        if first_byte == OPTION_MARKER_FOR_PRESENT_VALUE:
            self.general_codec.do_decode_nested(reader, value.value)
            return

        raise ValueError(f"invalid first byte for nested encoded option: {first_byte}")

    def decode_top_level(self, data: bytes, value: OptionValue):
        if len(data) == 0:
            value.value = None
            return

        first_byte = data[0]
        data_after_first_byte = data[1:]

        if first_byte != OPTION_MARKER_FOR_PRESENT_VALUE:
            raise ValueError(f"invalid first byte for top-level encoded option: {first_byte}")

        reader = io.BytesIO(data_after_first_byte)
        self.general_codec.do_decode_nested(reader, value.value)
