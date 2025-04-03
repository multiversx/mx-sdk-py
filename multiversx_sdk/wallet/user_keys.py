from typing import Optional

import nacl.signing

from multiversx_sdk.core.address import Address
from multiversx_sdk.wallet.constants import USER_PUBKEY_LENGTH, USER_SEED_LENGTH
from multiversx_sdk.wallet.errors import (
    InvalidPublicKeyLengthError,
    InvalidSecretKeyLengthError,
)


class UserSecretKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != USER_SEED_LENGTH:
            raise InvalidSecretKeyLengthError()

        self.buffer = buffer

    @classmethod
    def generate(cls) -> "UserSecretKey":
        signing_key = nacl.signing.SigningKey.generate()
        secret_key = bytes(signing_key)
        return cls(secret_key)

    @classmethod
    def new_from_string(cls, buffer_hex: str) -> "UserSecretKey":
        buffer = bytes.fromhex(buffer_hex)
        return cls(buffer)

    def generate_public_key(self) -> "UserPublicKey":
        public_key = bytes(nacl.signing.SigningKey(self.buffer).verify_key)
        return UserPublicKey(public_key)

    def sign(self, data: bytes) -> bytes:
        signing_key = nacl.signing.SigningKey(self.buffer)
        signed = signing_key.sign(data)
        signature = signed.signature
        return signature

    def hex(self) -> str:
        return self.buffer.hex()

    def get_bytes(self) -> bytes:
        return self.buffer

    def __str__(self) -> str:
        return UserSecretKey.__name__

    def __repr__(self) -> str:
        return UserSecretKey.__name__

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, UserSecretKey):
            return False

        return self.buffer == value.buffer


class UserPublicKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != USER_PUBKEY_LENGTH:
            raise InvalidPublicKeyLengthError()

        self.buffer = bytes(buffer)

    def verify(self, data: bytes, signature: bytes) -> bool:
        verify_key = nacl.signing.VerifyKey(self.buffer)

        try:
            verify_key.verify(data, signature)
            return True
        except Exception:
            return False

    def to_address(self, hrp: Optional[str] = None) -> Address:
        return Address(self.buffer, hrp)

    def get_bytes(self) -> bytes:
        return self.buffer

    def hex(self) -> str:
        return self.buffer.hex()

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return self.hex()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, UserPublicKey):
            return False

        return self.buffer == value.buffer
