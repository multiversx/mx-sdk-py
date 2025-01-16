import io
from typing import Any

from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.shared import convert_native_value_to_list


class TupleValue:
    def __init__(self, fields: list[ISingleValue]) -> None:
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

    def set_payload(self, value: Any):
        native_list, ok = convert_native_value_to_list(value, raise_on_failure=False)
        if ok:
            if len(self.fields) != len(native_list):
                raise ValueError(
                    f"the number of fields ({len(self.fields)}) does not match the number of provided native values ({len(native_list)})"
                )

            for i, field in enumerate(self.fields):
                field.set_payload(native_list[i])

            return

        raise ValueError("cannot set payload for tuple (should be either a tuple or a list)")

    def get_payload(self) -> Any:
        native_values = [field.get_payload() for field in self.fields]
        return tuple(native_values)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TupleValue) and self.fields == other.fields
