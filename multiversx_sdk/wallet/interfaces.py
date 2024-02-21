
from typing import Protocol

ISignature = bytes


class IRandomness(Protocol):
    salt: bytes
    iv: bytes
    id: str


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...
