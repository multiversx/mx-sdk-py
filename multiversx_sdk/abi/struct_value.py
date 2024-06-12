import io
from types import SimpleNamespace
from typing import Any, List

from multiversx_sdk.abi.fields import (Field, decode_fields_nested,
                                       encode_fields_nested,
                                       set_fields_from_dictionary,
                                       set_fields_from_list)
from multiversx_sdk.abi.shared import (convert_native_value_to_dictionary,
                                       convert_native_value_to_list)


class StructValue:
    def __init__(self, fields: List[Field]) -> None:
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
