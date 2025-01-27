import io
from typing import Any

from multiversx_sdk.abi.shared import decode_length, encode_length, read_bytes_exactly
from multiversx_sdk.core.constants import INTEGER_MAX_NUM_BYTES


class BigUIntValue:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        data = self._unsigned_to_bytes()
        encode_length(writer, len(data))
        writer.write(data)

    def encode_top_level(self, writer: io.BytesIO):
        data = self._unsigned_to_bytes()
        writer.write(data)

    def decode_nested(self, reader: io.BytesIO):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        self.value = self._unsigned_from_bytes(data)

    def decode_top_level(self, data: bytes):
        self.value = self._unsigned_from_bytes(data)

    def _unsigned_to_bytes(self) -> bytes:
        value = self.value

        if value == 0:
            return b""

        data = value.to_bytes(INTEGER_MAX_NUM_BYTES, byteorder="big", signed=False)
        data = data.lstrip(bytes([0]))
        return data

    def _unsigned_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=False)

    def set_payload(self, value: Any):
        self.value = int(value)

    def get_payload(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BigUIntValue) and self.value == other.value

    def __int__(self):
        return self.value
