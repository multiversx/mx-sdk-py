import io
from typing import Any, Callable, Optional

from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.shared import (
    convert_native_value_to_list,
    decode_length,
    encode_length,
)


class ListValue:
    def __init__(
        self,
        items: Optional[list[ISingleValue]] = None,
        item_creator: Optional[Callable[[], ISingleValue]] = None,
    ) -> None:
        self.items = items or []
        self.item_creator = item_creator

    def encode_nested(self, writer: io.BytesIO):
        encode_length(writer, len(self.items))
        self._encode_list_items(writer)

    def encode_top_level(self, writer: io.BytesIO):
        self._encode_list_items(writer)

    def decode_nested(self, reader: io.BytesIO):
        length = decode_length(reader)

        self.items = []
        for _ in range(length):
            self._decode_list_item(reader)

    def decode_top_level(self, data: bytes):
        reader = io.BytesIO(data)
        self.items = []

        while reader.tell() < len(data):
            self._decode_list_item(reader)

    def _encode_list_items(self, writer: io.BytesIO):
        for item in self.items:
            item.encode_nested(writer)

    def _decode_list_item(self, reader: io.BytesIO):
        if self.item_creator is None:
            raise Exception("cannot decode list: item creator is None")

        new_item = self.item_creator()
        new_item.decode_nested(reader)
        self.items.append(new_item)

    def set_payload(self, value: Any):
        if not self.item_creator:
            raise ValueError("populating a list from a native object requires the item creator to be set")

        native_items, _ = convert_native_value_to_list(value)

        self.items.clear()

        for native_item in native_items:
            item = self.item_creator()
            item.set_payload(native_item)
            self.items.append(item)

    def get_payload(self) -> Any:
        return [item.get_payload() for item in self.items]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ListValue) and self.items == other.items and self.item_creator == other.item_creator

    def __iter__(self) -> Any:
        return iter(self.items)
