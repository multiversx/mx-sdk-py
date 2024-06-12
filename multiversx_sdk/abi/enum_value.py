import io
from types import SimpleNamespace
from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.constants import ENUM_DISCRIMINANT_FIELD_NAME
from multiversx_sdk.abi.fields import (Field, decode_fields_nested,
                                       encode_fields_nested,
                                       set_fields_from_dictionary,
                                       set_fields_from_list)
from multiversx_sdk.abi.shared import (convert_native_value_to_dictionary,
                                       convert_native_value_to_list)
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

        encode_fields_nested(self.fields, writer)

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

        decode_fields_nested(self.fields, reader)

    def decode_top_level(self, data: bytes):
        if len(data) == 0:
            self.discriminant = 0
            return

        reader = io.BytesIO(data)
        self.decode_nested(reader)

    def set_payload(self, value: Any):
        if not self.fields_provider:
            raise ValueError("populating an enum from a native object requires the fields provider to be set")

        if isinstance(value, int):
            if self.fields_provider(value):
                raise ValueError("for enums, if the native object is a mere integer, it must be the discriminant, and the corresponding enum variant must have no fields")

            self.discriminant = value
            return

        native_dictionary, ok = convert_native_value_to_dictionary(value, raise_on_failure=False)
        if ok:
            if ENUM_DISCRIMINANT_FIELD_NAME not in native_dictionary:
                raise ValueError(f"for enums, the native object (when it's a dictionary) must contain the special field '{ENUM_DISCRIMINANT_FIELD_NAME}'")

            self.discriminant = int(native_dictionary[ENUM_DISCRIMINANT_FIELD_NAME])
            self.fields = self.fields_provider(self.discriminant)
            set_fields_from_dictionary(self.fields, native_dictionary)
            return

        native_list, ok = convert_native_value_to_list(value, raise_on_failure=False)
        if ok:
            if len(native_list) == 0 or not isinstance(native_list[0], int):
                raise ValueError("for enums, the native object (when it's a list) must have the discriminant as the first element")

            self.discriminant = int(native_list[0])
            self.fields = self.fields_provider(self.discriminant)
            set_fields_from_list(self.fields, native_list[1:])
            return

        raise ValueError("cannot set payload for enum (should be either a dictionary or a list)")

    def get_payload(self) -> Any:
        obj = SimpleNamespace()

        for field in self.fields:
            setattr(obj, field.name, field.get_payload())

        setattr(obj, ENUM_DISCRIMINANT_FIELD_NAME, self.discriminant)

        return obj

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, EnumValue)
            and self.discriminant == other.discriminant
            and self.fields == other.fields
        )

    def __iter__(self):
        yield (ENUM_DISCRIMINANT_FIELD_NAME, self.discriminant)

        for field in self.fields:
            yield (field.name, field.value)
