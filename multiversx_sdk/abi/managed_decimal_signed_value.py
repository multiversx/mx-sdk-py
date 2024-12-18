import io
from decimal import ROUND_DOWN, Decimal
from typing import Union

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.constants import U32_SIZE_IN_BYTES
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.small_int_values import U32Value


class ManagedDecimalSignedValue:
    def __init__(
        self, value: Union[float, str] = 0, scale: int = 0, is_variable: bool = False
    ) -> None:
        self.value = Decimal(value)
        self.scale = scale
        self.is_variable = is_variable

    def set_payload(self, value: Union[float, str]):
        self.value = Decimal(value)

    def get_payload(self) -> Decimal:
        return self.value

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def decode_top_level(self, data: bytes):
        if not len(data):
            return ManagedDecimalSignedValue(0, 0)

        if self.is_variable:
            big_uint_size = len(data) - U32_SIZE_IN_BYTES
            value = Decimal(self._unsigned_from_bytes(data[:big_uint_size]))
            data = data[big_uint_size + 1 :]
            self.scale = self._unsigned_from_bytes(data[:U32_SIZE_IN_BYTES])
            self.value = value.shift(-self.scale)
        else:
            self.value = Decimal(self._unsigned_from_bytes(data)).shift(-self.scale)

    def _unsigned_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=False)

    def encode_nested(self, writer: io.BytesIO):
        scaled_value = self.value * (10**self.scale)
        raw_value = BigUIntValue(int(scaled_value))

        if self.is_variable:
            raw_value.encode_nested(writer)
            U32Value(self.scale).encode_nested(writer)
        else:
            raw_value.encode_top_level(writer)

    def decode_nested(self, reader: io.BytesIO):
        length = self._unsigned_from_bytes(read_bytes_exactly(reader, U32_SIZE_IN_BYTES))
        payload = read_bytes_exactly(reader, length)
        self.decode_top_level(payload)

    def get_precision(self):
        formatted_value = self.value.quantize(Decimal(f"1.{'0' * self.scale}"), rounding=ROUND_DOWN)
        precision = len(str(formatted_value).replace(".", ""))
        return precision

    def to_string(self) -> str:
        formatted_value = self.value.quantize(Decimal(f"1.{'0' * self.scale}"), rounding=ROUND_DOWN)
        return str(formatted_value)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, ManagedDecimalSignedValue):
            return False

        if self.scale != value.scale:
            return False

        return self.value == value.value
