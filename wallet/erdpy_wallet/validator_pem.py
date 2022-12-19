from pathlib import Path

from erdpy_wallet import pem_format
from erdpy_wallet.validator_keys import ValidatorSecretKey


class ValidatorPEM:
    def __init__(self, label: str, secret_key: ValidatorSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> 'ValidatorPEM':
        entry = pem_format.parse(path, index)
        secret_key = ValidatorSecretKey(entry.message)
        return ValidatorPEM(entry.label, secret_key)

    def save(self, path: Path):
        message = self.secret_key.buffer
        pem_format.write(path, self.label, message)
