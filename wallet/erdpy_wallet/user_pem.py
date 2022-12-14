from pathlib import Path

from erdpy_core import Address

from erdpy_wallet import pem_format
from erdpy_wallet.constants import USER_SEED_LENGTH
from erdpy_wallet.user_keys import UserSecretKey


class UserPEM:
    def __init__(self, secret_key: UserSecretKey) -> None:
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> 'UserPEM':
        entry = pem_format.parse(path, index)
        secret_key = UserSecretKey(entry.message[0:USER_SEED_LENGTH])
        return UserPEM(secret_key)

    def save(self, path: Path, address_prefix: str):
        label = Address(self.public_key.buffer, address_prefix).bech32()
        message = self.secret_key.buffer + self.public_key.buffer
        pem_format.write(path, label, message)
