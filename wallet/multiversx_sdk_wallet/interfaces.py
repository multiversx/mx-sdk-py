
from typing import Protocol

ISignature = bytes


class ISignable(Protocol):
    def serialize_for_signing(self) -> bytes: ...


class IVerifiable(Protocol):
    signature: ISignature

    def serialize_for_signing(self) -> bytes: ...


class IUserWalletRandomness(Protocol):
    salt: bytes
    iv: bytes
    id: str


class IAddress(Protocol):
    def bech32(self) -> str: ...
