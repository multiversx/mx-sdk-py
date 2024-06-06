import io
from typing import Any, Dict, List

from multiversx_sdk.abi.interface import SingleValue


class Field:
    def __init__(self, name: str, value: SingleValue) -> None:
        self.name = name
        self.value = value


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


