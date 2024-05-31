import io
from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.field import Field
from multiversx_sdk.abi.small_int_values import U8Value


class EnumValue:
    def __init__(self,
                 discriminant: int = 0,
                 fields: Optional[List[Field]] = None,
                 fields_provider: Optional[Callable[[int], List[Field]]] = None) -> None:
        self.discriminant = discriminant
        self.fields = fields or []
        self.fields_provider = fields_provider

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
        if self.fields_provider is None:
            raise Exception("cannot decode enum: fields provider is None")

        discriminant = U8Value()
        discriminant.decode_nested(reader)
        self.discriminant = discriminant.value
        self.fields = self.fields_provider(self.discriminant)

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

    def set_native_object(self, value: Any):
        if not self.fields_provider:
            raise ValueError("populating an enum from a native object requires the fields provider to be set")

        try:
            native_dict = dict(value)
        except Exception:
            raise ValueError("cannot convert native value to dict")

        if "__discriminant__" not in native_dict:
            raise ValueError("for enums, the native object must contain the special field '__discriminant__'")

        self.discriminant = native_dict["__discriminant__"]
        self.fields = self.fields_provider(self.discriminant)

        for field in self.fields:
            if field.name not in native_dict:
                raise ValueError(f"the native object is missing the field '{field.name}'")

            native_field_value = native_dict[field.name]
            field.set_native_object(native_field_value)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, EnumValue)
            and self.discriminant == other.discriminant
            and self.fields == other.fields
        )
