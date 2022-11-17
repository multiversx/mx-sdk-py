from pathlib import Path

import nacl.signing
from erdpy_core.address import Address

from erdpy_wallet import pem
from erdpy_wallet.constants import USER_PUBKEY_LENGTH, USER_SEED_LENGTH
from erdpy_wallet.errors import ErrBadPublicKeyLength, ErrBadSecretKeyLength
from erdpy_wallet.interfaces import ISignature
from erdpy_wallet.interfaces_as_output import IAddressAsOutput
from erdpy_wallet.keyfile import load_from_key_file


class UserSecretKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != USER_SEED_LENGTH:
            raise ErrBadSecretKeyLength()

        self.buffer = buffer

    @classmethod
    def from_string(cls, buffer_hex: str) -> 'UserSecretKey':
        buffer = bytes.fromhex(buffer_hex)
        return UserSecretKey(buffer)

    @classmethod
    def from_pem_file(cls, path: Path, index: int) -> 'UserSecretKey':
        secret_key, _ = pem.parse(path, index)
        return UserSecretKey(secret_key)

    @classmethod
    def from_wallet_file(cls, path: Path, password: str) -> 'UserSecretKey':
        _, secret_key = load_from_key_file(path, password)
        return UserSecretKey(secret_key)

    def generate_public_key(self) -> 'UserPublicKey':
        public_key = bytes(nacl.signing.SigningKey(self.buffer).verify_key)
        return UserPublicKey(public_key)

    def sign(self, data: bytes) -> ISignature:
        signing_key = nacl.signing.SigningKey(self.buffer)
        signed = signing_key.sign(data)
        signature = signed.signature
        return signature

    def hex(self) -> str:
        return self.buffer.hex()

    def __str__(self) -> str:
        return UserSecretKey.__name__

    def __repr__(self) -> str:
        return UserSecretKey.__name__


class UserPublicKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != USER_PUBKEY_LENGTH:
            raise ErrBadPublicKeyLength()

        self.buffer = buffer

    def verify(self, data: bytes, signature: ISignature) -> bool:
        verify_key = nacl.signing.VerifyKey(self.buffer)

        try:
            verify_key.verify(data, signature)
            return True
        except Exception:
            return False

    def hex(self) -> str:
        return self.buffer.hex()

    def to_address(self) -> IAddressAsOutput:
        return Address(self.buffer)

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return self.hex()
