import io
from typing import Any, List

from multiversx_sdk.abi.field import Field
from multiversx_sdk.abi.small_int_values import U8Value


class EnumValue:
    def __init__(self, discriminant: int, fields: List[Field]) -> None:
        self.discriminant = discriminant
        self.fields = fields

    def encode_nested(self, writer: io.BytesIO):
        discriminant = U8Value(self.discriminant)
        discriminant.encode_nested(writer)

        for field in self.fields:
            try:
                field.value.encode_nested(writer)
            except Exception as e:
                raise Exception(f"cannot encode field '{field.name}' of enum, because of: {e}")

    def encode_top_level(self, writer: io.BytesIO):
        if self.discriminant == 0 and len(self.fields) == 0:
            # Write nothing
            return

        self.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        discriminant = U8Value()
        discriminant.decode_nested(reader)
        self.discriminant = discriminant.value

        for field in self.fields:
            try:
                field.value.decode_nested(reader)
            except Exception as e:
                raise Exception(f"cannot decode field '{field.name}' of enum, because of: {e}")

    def decode_top_level(self, data: bytes):
        if len(data) == 0:
            self.discriminant = 0
            return

        reader = io.BytesIO(data)
        self.decode_nested(reader)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, EnumValue)
            and self.discriminant == other.discriminant
            and self.fields == other.fields
        )
