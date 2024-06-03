import io
from typing import Any, List

from multiversx_sdk.abi.field import Field


class StructValue:
    def __init__(self, fields: List[Field]) -> None:
        self.fields = fields

    def encode_nested(self, writer: io.BytesIO):
        for field in self.fields:
            try:
                field.value.encode_nested(writer)
            except Exception as e:
                raise Exception(f"cannot encode field '{field.name}' of struct, because of: {e}")

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        for field in self.fields:
            try:
                field.value.decode_nested(reader)
            except Exception as e:
                raise Exception(f"cannot decode field '{field.name}' of struct, because of: {e}")

    def decode_top_level(self, data: bytes):
        reader = io.BytesIO(data)
        self.decode_nested(reader)

    def set_native_object(self, value: Any):
        try:
            native_dict = dict(value)
        except Exception:
            raise ValueError("cannot convert native value to dict")

        for field in self.fields:
            if field.name not in native_dict:
                raise ValueError(f"the native object is missing the field '{field.name}'")

            native_field_value = native_dict[field.name]

            try:
                field.set_native_object(native_field_value)
            except Exception as e:
                raise ValueError(f"cannot set native object for field '{field.name}' of struct, because of: {e}")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StructValue) and self.fields == other.fields
