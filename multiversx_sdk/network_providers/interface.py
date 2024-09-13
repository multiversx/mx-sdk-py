from typing import Any, Dict, Protocol


class ISerializable(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        ...


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


class IPagination(Protocol):
    def get_start(self) -> int:
        ...

    def get_size(self) -> int:
        ...
