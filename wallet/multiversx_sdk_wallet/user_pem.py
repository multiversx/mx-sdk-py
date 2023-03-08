from pathlib import Path
from typing import List

from multiversx_sdk_wallet import pem_format
from multiversx_sdk_wallet.constants import USER_SEED_LENGTH
from multiversx_sdk_wallet.user_keys import UserSecretKey


class UserPEM:
    def __init__(self, label: str, secret_key: UserSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> 'UserPEM':
        return cls.from_file_all(path)[index]

    @classmethod
    def from_file_all(cls, path: Path) -> List['UserPEM']:
        text = path.expanduser().resolve().read_text()
        return cls.from_text_all(text)

    @classmethod
    def from_text(cls, text: str, index: int = 0) -> 'UserPEM':
        items = cls.from_text_all(text)
        return items[index]

    @classmethod
    def from_text_all(cls, text: str) -> List['UserPEM']:
        entries = pem_format.parse_text(text)
        secret_keys = [UserSecretKey(entry.message[0:USER_SEED_LENGTH]) for entry in entries]
        labels = [entry.label for entry in entries]
        items = [UserPEM(label, secret_key) for label, secret_key in zip(labels, secret_keys)]
        return items

    def save(self, path: Path):
        message = self.secret_key.buffer + self.public_key.buffer
        pem_format.write(path, self.label, message)
