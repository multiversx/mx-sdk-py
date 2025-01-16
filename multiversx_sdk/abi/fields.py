import io
from typing import Any

from multiversx_sdk.abi.interface import ISingleValue


class Field:
    def __init__(self, name: str, value: ISingleValue) -> None:
        self.name = name
        self.value = value

    def set_payload(self, value: Any):
        self.value.set_payload(value)

    def get_payload(self) -> Any:
        return self.value.get_payload()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Field) and self.name == other.name and self.value == other.value


def encode_fields_nested(fields: list[Field], writer: io.BytesIO):
    for field in fields:
        try:
            field.value.encode_nested(writer)
        except Exception as e:
            raise Exception(f"cannot encode field '{field.name}', because of: {e}")


def decode_fields_nested(fields: list[Field], reader: io.BytesIO):
    for field in fields:
        try:
            field.value.decode_nested(reader)
        except Exception as e:
            raise Exception(f"cannot decode field '{field.name}', because of: {e}")


def set_fields_from_dictionary(fields: list[Field], dictionary: dict[str, Any]):
    for field in fields:
        if field.name not in dictionary:
            raise ValueError(f"the dictionary is missing the key '{field.name}'")

        field_payload = dictionary[field.name]

        try:
            field.set_payload(field_payload)
        except Exception as error:
            raise ValueError(f"cannot set payload for field '{field.name}', because of: {error}")


def set_fields_from_list(fields: list[Field], items: list[Any]):
    if len(fields) != len(items):
        raise ValueError(
            f"the number of fields ({len(fields)}) does not match the number of provided items ({len(items)})"
        )

    for index, field in enumerate(fields):
        field_payload = items[index]

        try:
            field.set_payload(field_payload)
        except Exception as error:
            raise ValueError(f"cannot set payload for field '{field.name}', because of: {error}")
