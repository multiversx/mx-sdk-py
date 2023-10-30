
from typing import Protocol

ISignature = bytes


class IRandomness(Protocol):
    salt: bytes
    iv: bytes
    id: str


class IAddress(Protocol):
    def bech32(self) -> str: ...
