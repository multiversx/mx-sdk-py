import io

from multiversx_sdk.abi.constants import FALS_AS_BYTE, TRUE_AS_BYTE
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.values_single import BoolValue


def encode_nested_bool(writer: io.BytesIO, value: BoolValue):
    if value.value:
        writer.write(bytes([TRUE_AS_BYTE]))
        return

    writer.write(bytes([FALS_AS_BYTE]))


def encode_top_level_bool(writer: io.BytesIO, value: BoolValue):
    if value.value:
        writer.write(bytes([TRUE_AS_BYTE]))

    # For "false", write nothing.


def decode_nested_bool(reader: io.BytesIO, value: BoolValue):
    data = read_bytes_exactly(reader, 1)
    value.value = byte_to_bool(data[0])


def decode_top_level_bool(data: bytes, value: BoolValue):
    if len(data) == 0:
        value.value = False
        return

    if len(data) == 1:
        value.value = byte_to_bool(data[0])
        return

    raise ValueError(f"unexpected boolean value: {data}")


def byte_to_bool(data: int) -> bool:
    if data == TRUE_AS_BYTE:
        return True

    if data == FALS_AS_BYTE:
        return False

    raise ValueError(f"unexpected boolean value: {data}")
