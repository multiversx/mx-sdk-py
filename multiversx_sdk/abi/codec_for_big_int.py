
import io

from multiversx_sdk.abi.interface import INumericalValue
from multiversx_sdk.abi.shared import (decode_length, encode_length,
                                       read_bytes_exactly)
from multiversx_sdk.core.constants import INTEGER_MAX_NUM_BYTES


class CodecForBigInt:
    def encode_nested_unsigned(self, writer: io.BytesIO, value: int):
        data = self._unsigned_to_bytes(value)
        encode_length(writer, len(data))
        writer.write(data)

    def encode_nested_signed(self, writer: io.BytesIO, value: int):
        data = self._signed_to_bytes(value)
        encode_length(writer, len(data))
        writer.write(data)

    def encode_top_level_unsigned(self, writer: io.BytesIO, value: int):
        data = self._unsigned_to_bytes(value)
        writer.write(data)

    def encode_top_level_signed(self, writer: io.BytesIO, value: int):
        data = self._signed_to_bytes(value)
        writer.write(data)

    def decode_nested_unsigned(self, reader: io.BytesIO, value: INumericalValue):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        value.value = self._unsigned_from_bytes(data)

    def decode_nested_signed(self, reader: io.BytesIO, value: INumericalValue):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        value.value = self._signed_from_bytes(data)

    def decode_top_level_unsigned(self, data: bytes, value: INumericalValue):
        value.value = self._unsigned_from_bytes(data)

    def decode_top_level_signed(self, data: bytes, value: INumericalValue):
        value.value = self._signed_from_bytes(data)

    def _unsigned_to_bytes(self, value: int) -> bytes:
        if value == 0:
            return b''

        data = value.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big", signed=False)
        data = data.lstrip(bytes([0]))
        return data

    def _signed_to_bytes(self, value: int) -> bytes:
        if value == 0:
            return b''

        length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
        data = value.to_bytes(length, byteorder="big", signed=True)
        return data

    def _unsigned_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=False)

    def _signed_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=True)
