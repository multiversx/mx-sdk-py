import io
from typing import Any, List

from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.shared import convert_native_value_to_list


class TupleValue:
    def __init__(self, fields: List[ISingleValue]) -> None:
        self.fields = fields

    def encode_nested(self, writer: io.BytesIO):
        for i, field in enumerate(self.fields):
            try:
                field.encode_nested(writer)
            except Exception as e:
                raise Exception(f"cannot encode field '{i}' of tuple, because of: {e}")

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        for i, field in enumerate(self.fields):
            try:
                field.decode_nested(reader)
            except Exception as e:
                raise Exception(f"cannot decode field '{i}' of tuple, because of: {e}")

    def decode_top_level(self, data: bytes):
        reader = io.BytesIO(data)
        self.decode_nested(reader)

