import io
from typing import Any

from multiversx_sdk.abi.constants import NUM_BYTES_IN_64_BITS
from multiversx_sdk.abi.shared import read_bytes_exactly


class SmallUIntValue:
    def __init__(self, num_bytes: int, value: int = 0) -> None:
        self._num_bytes = num_bytes
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        data = self.value.to_bytes(self._num_bytes, byteorder="big", signed=False)
        writer.write(data)

    def encode_top_level(self, writer: io.BytesIO):
        value = self.value

        if value == 0:
            return

        data = value.to_bytes(NUM_BYTES_IN_64_BITS, byteorder="big", signed=False)
        data = data.lstrip(bytes([0]))
        writer.write(data)

    def decode_nested(self, reader: io.BytesIO):
        data = read_bytes_exactly(reader, self._num_bytes)
        self.value = int.from_bytes(data, byteorder="big", signed=False)

    def decode_top_level(self, data: bytes):
        self.value = int.from_bytes(data, byteorder="big", signed=False)

        # Do a simple bounds check.
        try:
            self.value.to_bytes(self._num_bytes, byteorder="big", signed=False)
        except OverflowError:
            raise ValueError(
                f"decoded value is too large or invalid (does not fit into {self._num_bytes} byte(s)): {self.value}"
            )

    def set_payload(self, value: Any):
        self.value = int(value)

    def get_payload(self) -> Any:
        return self.value

    def __int__(self):
        return self.value


class SmallIntValue:
    def __init__(self, num_bytes: int, value: int = 0) -> None:
        self._num_bytes = num_bytes
        self.value = value

    def encode_nested(self, writer: io.BytesIO):
        data = self.value.to_bytes(self._num_bytes, byteorder="big", signed=True)
        writer.write(data)

    def encode_top_level(self, writer: io.BytesIO):
        value = self.value

        if value == 0:
            return

        length = ((value + (value < 0)).bit_length() + 7 + 1) // 8
        data = value.to_bytes(length, byteorder="big", signed=True)
        writer.write(data)

    def decode_nested(self, reader: io.BytesIO):
        data = read_bytes_exactly(reader, self._num_bytes)
        self.value = int.from_bytes(data, byteorder="big", signed=True)

    def decode_top_level(self, data: bytes):
        self.value = int.from_bytes(data, byteorder="big", signed=True)

        # Do a simple bounds check.
        try:
            self.value.to_bytes(self._num_bytes, byteorder="big", signed=True)
        except OverflowError:
            raise ValueError(
                f"decoded value is too large or invalid (does not fit into {self._num_bytes} byte(s)): {self.value}"
            )

    def set_payload(self, value: Any):
        self.value = int(value)

    def get_payload(self) -> Any:
        return self.value

    def __int__(self):
        return self.value


class U8Value(SmallUIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(1, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U8Value) and self.value == other.value


class U16Value(SmallUIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(2, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U16Value) and self.value == other.value


class U32Value(SmallUIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(4, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U32Value) and self.value == other.value


class U64Value(SmallUIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(8, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U64Value) and self.value == other.value


class I8Value(SmallIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(1, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I8Value) and self.value == other.value


class I16Value(SmallIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(2, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I16Value) and self.value == other.value


class I32Value(SmallIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(4, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I32Value) and self.value == other.value


class I64Value(SmallIntValue):
    def __init__(self, value: int = 0) -> None:
        super().__init__(8, value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I64Value) and self.value == other.value
