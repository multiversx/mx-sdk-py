import io
from typing import Any, Protocol, runtime_checkable


class IPayloadHolder(Protocol):
    def set_payload(self, value: Any):
        ...

    def get_payload(self) -> Any:
        ...


@runtime_checkable
class ISingleValue(IPayloadHolder, Protocol):
    def encode_nested(self, writer: io.BytesIO):
        ...

    def encode_top_level(self, writer: io.BytesIO):
        ...

    def decode_nested(self, reader: io.BytesIO):
        ...

    def decode_top_level(self, data: bytes):
        ...
