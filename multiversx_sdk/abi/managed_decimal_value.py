import io
from decimal import ROUND_DOWN, Decimal
from typing import Any, Union

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.constants import U32_SIZE_IN_BYTES
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.small_int_values import U32Value


class ManagedDecimalValue:
    def __init__(self, value: Union[int, str] = 0, scale: int = 0, is_variable: bool = False):
        self.value = Decimal(value)
        self.scale = scale
        self.is_variable = is_variable

    def set_payload(self, value: Any):
        if isinstance(value, ManagedDecimalValue):
            if self.is_variable != value.is_variable:
                raise Exception("Cannot set payload! Both ManagedDecimalValues should be variable.")

            self.value = value.value

            if self.is_variable:
                self.scale = value.scale
        else:
            self.value = self._convert_to_decimal(value)

    def get_payload(self) -> Decimal:
        return self.value

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def encode_nested(self, writer: io.BytesIO):
        raw_value = BigUIntValue(self._convert_value_to_int())
        if self.is_variable:
            raw_value.encode_nested(writer)
            U32Value(self.scale).encode_nested(writer)
        else:
            raw_value.encode_top_level(writer)

    def decode_top_level(self, data: bytes):
        if not data:
            self.value = Decimal(0)
            self.scale = 0
            return

        biguint = BigUIntValue()
        scale = U32Value()

        if self.is_variable:
            # read biguint value length in bytes
            big_uint_size = self._unsigned_from_bytes(data[:U32_SIZE_IN_BYTES])

            # remove biguint length; data is only biguint value and scale
            data = data[U32_SIZE_IN_BYTES:]

            # read biguint value
            biguint.decode_top_level(data[:big_uint_size])

            # remove biguintvalue; data contains only scale
            data = data[big_uint_size:]

            # read scale
            scale.decode_top_level(data)
            self.scale = scale.get_payload()
        else:
            biguint.decode_top_level(data)

        self.value = self._convert_to_decimal(biguint.get_payload())

    def decode_nested(self, reader: io.BytesIO):
        length = self._unsigned_from_bytes(read_bytes_exactly(reader, U32_SIZE_IN_BYTES))
        payload = read_bytes_exactly(reader, length)
        self.decode_top_level(payload)

    def to_string(self) -> str:
        value_str = str(self._convert_value_to_int())
        if self.scale == 0:
            return value_str
        if len(value_str) <= self.scale:
            # If the value is smaller than the scale, prepend zeros
            value_str = "0" * (self.scale - len(value_str) + 1) + value_str
        return f"{value_str[:-self.scale]}.{value_str[-self.scale:]}"

    def get_precision(self) -> int:
        return len(str(self._convert_value_to_int()).lstrip("0"))

    def _unsigned_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=False)

    def _convert_value_to_int(self) -> int:
        scaled_value: Decimal = self.value * (10**self.scale)
        return int(scaled_value.quantize(Decimal("1."), rounding=ROUND_DOWN))

    def _convert_to_decimal(self, value: Union[int, str]) -> Decimal:
        return Decimal(value) / (10**self.scale)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManagedDecimalValue):
            return False
        return self.value == other.value and self.scale == other.scale
