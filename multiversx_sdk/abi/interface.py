import io
from typing import Protocol


class SingleValue(Protocol):
    def encode_nested(self, writer: io.BytesIO):
        ...

    def encode_top_level(self, writer: io.BytesIO):
        ...

    def decode_nested(self, reader: io.BytesIO):
        ...

    def decode_top_level(self, data: bytes):
        ...
