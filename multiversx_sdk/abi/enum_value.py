import io
from types import SimpleNamespace
from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.fields import (Field, decode_fields_nested,
                                       encode_fields_nested,
                                       set_fields_from_native_dictionary,
                                       set_fields_from_native_list)
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
