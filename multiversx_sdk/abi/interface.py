import io
from typing import Any, Protocol


class ICodec(Protocol):
    """
    For internal use only.
    """

    def do_encode_nested(self, writer: io.BytesIO, value: Any) -> None:
        ...

    def do_decode_nested(self, reader: io.BytesIO, value: Any) -> None:
        ...

    @property
    def pubkey_length(self) -> int:
        ...


class INumericalValue(Protocol):
    """
    For internal use only.
    """

    @property
    def value(self) -> int:
        ...

    @value.setter
    def value(self, value: int) -> None:
        ...
