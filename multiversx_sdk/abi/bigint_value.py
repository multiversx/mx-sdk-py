import io
from typing import Any

from multiversx_sdk.abi.shared import decode_length, encode_length, read_bytes_exactly


class BigIntValue:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        data = self._signed_to_bytes()
        encode_length(writer, len(data))
        writer.write(data)

    def encode_top_level(self, writer: io.BytesIO):
        data = self._signed_to_bytes()
        writer.write(data)

    def decode_nested(self, reader: io.BytesIO):
        length = decode_length(reader)
        data = read_bytes_exactly(reader, length)
        self.value = self._signed_from_bytes(data)

    def decode_top_level(self, data: bytes):
        self.value = self._signed_from_bytes(data)

    def _signed_to_bytes(self) -> bytes:
        value = self.value

        if value == 0:
            return b""

        length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
        data = value.to_bytes(length, byteorder="big", signed=True)
        return data

    def _signed_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=True)

    def set_payload(self, value: Any):
        self.value = int(value)

    def get_payload(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BigIntValue) and self.value == other.value

    def __int__(self):
        return self.value
