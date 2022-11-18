
from typing import Protocol

ISignature = bytes


class ISignable(Protocol):
    def serialize_for_signing(self) -> bytes:
        return bytes()


class IVerifiable(Protocol):
    def serialize_for_signing(self) -> bytes:
        return bytes()

    def get_signature(self) -> ISignature:
        return bytes()


class IUserWalletRandomness(Protocol):
    def get_salt(self) -> bytes:
        return bytes()

    def get_iv(self) -> bytes:
        return bytes()

    def get_id(self) -> str:
        return ""


class IAddress(Protocol):
    def bech32(self) -> str:
        return ""
