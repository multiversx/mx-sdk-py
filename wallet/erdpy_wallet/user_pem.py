from pathlib import Path

from erdpy_wallet import pem_format
from erdpy_wallet.constants import USER_SEED_LENGTH
from erdpy_wallet.user_keys import UserSecretKey


class UserPEM:
    def __init__(self, label: str, secret_key: UserSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> 'UserPEM':
        entry = pem_format.parse(path, index)
        secret_key = UserSecretKey(entry.message[0:USER_SEED_LENGTH])
        return UserPEM(entry.label, secret_key)

    def save(self, path: Path):
        message = self.secret_key.buffer + self.public_key.buffer
        pem_format.write(path, self.label, message)
