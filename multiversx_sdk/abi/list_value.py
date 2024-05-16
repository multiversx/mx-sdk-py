import io
from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.interface import SingleValue
from multiversx_sdk.abi.shared import decode_length, encode_length


class ListValue:
    def __init__(self,
                 items: Optional[List[SingleValue]] = None,
                 item_creator: Optional[Callable[[], SingleValue]] = None) -> None:
        self.items = items or []
        self.item_creator = item_creator

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ListValue)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )

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
