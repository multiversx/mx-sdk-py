import io
from types import SimpleNamespace
from typing import Any

from multiversx_sdk.abi.fields import (
    Field,
    decode_fields_nested,
    encode_fields_nested,
    set_fields_from_dictionary,
    set_fields_from_list,
)
from multiversx_sdk.abi.shared import (
    convert_native_value_to_dictionary,
    convert_native_value_to_list,
)


class StructValue:
    def __init__(self, fields: list[Field]) -> None:
        self.fields = fields

    def encode_nested(self, writer: io.BytesIO):
        encode_fields_nested(self.fields, writer)

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        decode_fields_nested(self.fields, reader)

    def decode_top_level(self, data: bytes):
        reader = io.BytesIO(data)
        self.decode_nested(reader)

    def set_payload(self, value: Any):
        native_dictionary, ok = convert_native_value_to_dictionary(value, raise_on_failure=False)
        if ok:
            set_fields_from_dictionary(self.fields, native_dictionary)
            return

        native_list, ok = convert_native_value_to_list(value, raise_on_failure=False)
        if ok:
            set_fields_from_list(self.fields, native_list)
            return

        raise ValueError("cannot set payload for struct (should be either a dictionary or a list)")

    def get_payload(self) -> Any:
        obj = SimpleNamespace()

        for field in self.fields:
            setattr(obj, field.name, field.get_payload())

        return obj

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StructValue) and self.fields == other.fields

    def __iter__(self):
        for field in self.fields:
            yield (field.name, field.value)
