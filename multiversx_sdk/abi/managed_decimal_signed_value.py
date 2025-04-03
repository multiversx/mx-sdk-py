import io
from decimal import Decimal, localcontext
from typing import Any, Union

from multiversx_sdk.abi.bigint_value import BigIntValue
from multiversx_sdk.abi.constants import (
    LOCAL_CONTEXT_PRECISION_FOR_DECIMAL,
    U32_SIZE_IN_BYTES,
)
from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.abi.small_int_values import U32Value


class ManagedDecimalSignedValue:
    def __init__(self, value: Union[int, str] = 0, scale: int = 0, is_variable: bool = False):
        self.value = Decimal(value)
        self.scale = scale
        self.is_variable = is_variable

    def set_payload(self, value: Any):
        if isinstance(value, ManagedDecimalSignedValue):
            if self.is_variable != value.is_variable:
                raise Exception("Cannot set payload! Both managed decimal values should be variable.")

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
        raw_value = BigIntValue(self._convert_value_to_int())
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

        value = BigIntValue()
        scale = U32Value()

        if self.is_variable:
            # read biguint value length in bytes
            value_length = self._unsigned_from_bytes(data[:U32_SIZE_IN_BYTES])

            # remove biguint length; data is only biguint value and scale
            data = data[U32_SIZE_IN_BYTES:]

            # read biguint value
            value.decode_top_level(data[:value_length])

            # remove biguintvalue; data contains only scale
            data = data[value_length:]

            # read scale
            scale.decode_top_level(data)
            self.scale = scale.get_payload()
        else:
            value.decode_top_level(data)

        self.value = self._convert_to_decimal(value.get_payload())

    def decode_nested(self, reader: io.BytesIO):
        length = self._unsigned_from_bytes(read_bytes_exactly(reader, U32_SIZE_IN_BYTES))
        payload = read_bytes_exactly(reader, length)
        self.decode_top_level(payload)

    def get_precision(self) -> int:
        value_str = f"{self.value:.{self.scale}f}"
        return len(value_str.replace(".", ""))

    def _unsigned_from_bytes(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big", signed=False)

    def _convert_value_to_int(self) -> int:
        with localcontext() as ctx:
            ctx.prec = LOCAL_CONTEXT_PRECISION_FOR_DECIMAL
            return int(self.value.scaleb(self.scale))

    def _convert_to_decimal(self, value: Union[int, str]) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = LOCAL_CONTEXT_PRECISION_FOR_DECIMAL
            return Decimal(value) / (10**self.scale)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManagedDecimalSignedValue):
            return False
        return self.value == other.value and self.scale == other.scale
