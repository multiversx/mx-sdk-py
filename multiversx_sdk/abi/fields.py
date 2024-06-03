import io
from typing import Any, Dict, List

from multiversx_sdk.abi.interface import SingleValue


class Field:
    def __init__(self, name: str, value: SingleValue) -> None:
        self.name = name
        self.value = value

    def set_native_object(self, value: Any):
        self.value.set_native_object(value)

    def get_native_object(self) -> Any:
        return self.value.get_native_object()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Field) and self.name == other.name and self.value == other.value


def encode_fields_nested(fields: List[Field], writer: io.BytesIO):
    for field in fields:
        try:
            field.value.encode_nested(writer)
        except Exception as e:
            raise Exception(f"cannot encode field '{field.name}', because of: {e}")


def decode_fields_nested(fields: List[Field], reader: io.BytesIO):
    for field in fields:
        try:
            field.value.decode_nested(reader)
        except Exception as e:
            raise Exception(f"cannot decode field '{field.name}', because of: {e}")


def set_fields_from_native_dictionary(fields: List[Field], native_dictionary: Dict[str, Any]):
    for field in fields:
        if field.name not in native_dictionary:
            raise ValueError(f"the native object is missing the field '{field.name}'")

        native_field_value = native_dictionary[field.name]

        try:
            field.set_native_object(native_field_value)
        except Exception as error:
            raise ValueError(f"cannot set native object for field '{field.name}', because of: {error}")


def set_fields_from_native_list(fields: List[Field], native_list: List[Any]):
    if len(fields) != len(native_list):
        raise ValueError(f"the number of fields ({len(fields)}) does not match the number of provided native values ({len(native_list)})")

    for index, field in enumerate(fields):
        native_field_value = native_list[index]

        try:
            field.set_native_object(native_field_value)
        except Exception as error:
            raise ValueError(f"cannot set native object for field '{field.name}', because of: {error}")
