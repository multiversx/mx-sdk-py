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
