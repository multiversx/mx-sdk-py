import io
from typing import Any, Protocol, runtime_checkable


class NativeObjectHolder(Protocol):
    def set_native_object(self, value: Any):
        ...

    def get_native_object(self) -> Any:
        ...


@runtime_checkable
class SingleValue(NativeObjectHolder, Protocol):
    def encode_nested(self, writer: io.BytesIO):
        ...

    def encode_top_level(self, writer: io.BytesIO):
        ...

    def decode_nested(self, reader: io.BytesIO):
        ...

    def decode_top_level(self, data: bytes):
        ...
