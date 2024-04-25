from typing import Any, Protocol


class ICodec(Protocol):
    """
    For internal use only.
    """

    def encode_nested(self, value: Any) -> bytes:
        ...

    @property
    def pubkey_length(self) -> int:
        ...
