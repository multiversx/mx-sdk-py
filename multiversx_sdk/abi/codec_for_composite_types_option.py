import io

from multiversx_sdk.abi.constants import (OPTION_MARKER_FOR_ABSENT_VALUE,
                                          OPTION_MARKER_FOR_PRESENT_VALUE)
from multiversx_sdk.abi.interface import ICodec
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.values_single import OptionValue


def encode_nested_option(codec: ICodec, writer: io.BytesIO, value: OptionValue):
    if value.value is None:
        writer.write(bytes([OPTION_MARKER_FOR_ABSENT_VALUE]))
        return

    writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
    codec.do_encode_nested(writer, value.value)


def encode_top_level_option(codec: ICodec, writer: io.BytesIO, value: OptionValue):
    if value.value is None:
        return

    writer.write(bytes([OPTION_MARKER_FOR_PRESENT_VALUE]))
    codec.do_encode_nested(writer, value.value)


def decode_nested_option(codec: ICodec, reader: io.BytesIO, value: OptionValue):
    data = read_bytes_exactly(reader, 1)
    first_byte = data[0]

    if first_byte == OPTION_MARKER_FOR_ABSENT_VALUE:
        value.value = None
        return

    if first_byte == OPTION_MARKER_FOR_PRESENT_VALUE:
        codec.do_decode_nested(reader, value.value)
        return

    raise ValueError(f"invalid first byte for nested encoded option: {first_byte}")


def decode_top_level_option(codec: ICodec, data: bytes, value: OptionValue):
    if len(data) == 0:
        value.value = None
        return

    first_byte = data[0]
    data_after_first_byte = data[1:]

    if first_byte != OPTION_MARKER_FOR_PRESENT_VALUE:
        raise ValueError(f"invalid first byte for top-level encoded option: {first_byte}")

    reader = io.BytesIO(data_after_first_byte)
    codec.do_decode_nested(reader, value.value)
