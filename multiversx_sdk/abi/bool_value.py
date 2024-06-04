import io
from typing import Any

from multiversx_sdk.abi.constants import FALS_AS_BYTE, TRUE_AS_BYTE
from multiversx_sdk.abi.shared import read_bytes_exactly


class BoolValue:
    def __init__(self, value: bool = False) -> None:
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        if self.value:
            writer.write(bytes([TRUE_AS_BYTE]))
            return

        writer.write(bytes([FALS_AS_BYTE]))

    def encode_top_level(self, writer: io.BytesIO):
        if self.value:
            writer.write(bytes([TRUE_AS_BYTE]))

        # For "false", write nothing.

    def decode_nested(self, reader: io.BytesIO):
        data = read_bytes_exactly(reader, 1)
        self.value = self._byte_to_bool(data[0])

    def decode_top_level(self, data: bytes):
        if len(data) == 0:
            self.value = False
            return

        if len(data) == 1:
            self.value = self._byte_to_bool(data[0])
            return

        raise ValueError(f"unexpected boolean value: {data}")

    def _byte_to_bool(self, data: int) -> bool:
        if data == TRUE_AS_BYTE:
            return True

        if data == FALS_AS_BYTE:
            return False

        raise ValueError(f"unexpected boolean value: {data}")

    def set_payload(self, value: Any):
        self.value = bool(value)

    def get_payload(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BoolValue) and self.value == other.value

    def __bool__(self) -> bool:
        return self.value
