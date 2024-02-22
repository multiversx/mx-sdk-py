import nacl.signing

from multiversx_sdk.core.address import Address
from multiversx_sdk.wallet.constants import (USER_PUBKEY_LENGTH,
                                             USER_SEED_LENGTH)
from multiversx_sdk.wallet.errors import (ErrBadPublicKeyLength,
                                          ErrBadSecretKeyLength)
from multiversx_sdk.wallet.interfaces import ISignature


class UserSecretKey:
    def __init__(self, buffer: bytes) -> None:
        if len(buffer) != USER_SEED_LENGTH:
            raise ErrBadSecretKeyLength()

        self.buffer = buffer

    @classmethod
    def generate(cls) -> 'UserSecretKey':
        signing_key = nacl.signing.SigningKey.generate()
        secret_key = bytes(signing_key)
        return UserSecretKey(secret_key)

    @classmethod
    def from_string(cls, buffer_hex: str) -> 'UserSecretKey':
        buffer = bytes.fromhex(buffer_hex)
        return UserSecretKey(buffer)

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

        self.buffer = bytes(buffer)

    def verify(self, data: bytes, signature: ISignature) -> bool:
        verify_key = nacl.signing.VerifyKey(self.buffer)

        try:
            verify_key.verify(data, signature)
            return True
        except Exception:
            return False

    def to_address(self, hrp: str) -> Address:
        return Address(self.buffer, hrp)

    def hex(self) -> str:
        return self.buffer.hex()

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return self.hex()
