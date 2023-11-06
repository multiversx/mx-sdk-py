
from typing import Protocol

ISignature = bytes


class IRandomness(Protocol):
    salt: bytes
    iv: bytes
    id: str


class IAddress(Protocol):
    def bech32(self) -> str: ...
    # `to_bech32()` will replace the above method in v1.0.0, when the packages will be merged together
