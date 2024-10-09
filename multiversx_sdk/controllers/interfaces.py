from typing import Protocol


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


class IAccount(Protocol):
    @property
    def address(self) -> IAddress:
        ...

    def sign(self, data: bytes) -> bytes:
        ...
