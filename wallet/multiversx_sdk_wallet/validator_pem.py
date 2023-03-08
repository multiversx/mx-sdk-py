from pathlib import Path
from typing import List

from multiversx_sdk_wallet import pem_format
from multiversx_sdk_wallet.validator_keys import ValidatorSecretKey


class ValidatorPEM:
    def __init__(self, label: str, secret_key: ValidatorSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> 'ValidatorPEM':
        return cls.from_file_all(path)[index]

    @classmethod
    def from_file_all(cls, path: Path) -> List['ValidatorPEM']:
        text = path.expanduser().resolve().read_text()
        return cls.from_text_all(text)

    @classmethod
    def from_text(cls, text: str, index: int = 0) -> 'ValidatorPEM':
        items = cls.from_text_all(text)
        return items[index]

    @classmethod
    def from_text_all(cls, text: str) -> List['ValidatorPEM']:
        entries = pem_format.parse_text(text)
        secret_keys = [ValidatorSecretKey(entry.message) for entry in entries]
        labels = [entry.label for entry in entries]
        items = [ValidatorPEM(label, secret_key) for label, secret_key in zip(labels, secret_keys)]
        return items

    def save(self, path: Path):
        message = self.secret_key.buffer
        pem_format.write(path, self.label, message)
