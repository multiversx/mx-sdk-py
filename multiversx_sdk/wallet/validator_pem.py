from pathlib import Path

from multiversx_sdk.wallet.pem_entry import PemEntry
from multiversx_sdk.wallet.validator_keys import ValidatorSecretKey


class ValidatorPEM:
    def __init__(self, label: str, secret_key: ValidatorSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> "ValidatorPEM":
        return cls.from_file_all(path)[index]

    @classmethod
    def from_file_all(cls, path: Path) -> list["ValidatorPEM"]:
        text = path.expanduser().resolve().read_text()
        return cls.from_text_all(text)

    @classmethod
    def from_text(cls, text: str, index: int = 0) -> "ValidatorPEM":
        items = cls.from_text_all(text)
        return items[index]

    @classmethod
    def from_text_all(cls, text: str) -> list["ValidatorPEM"]:
        entries = PemEntry.from_text_all(text)
        result_items: list[ValidatorPEM] = []

        for entry in entries:
            secret_key = ValidatorSecretKey(entry.message)
            item = cls(entry.label, secret_key)
            result_items.append(item)

        return result_items

    def save(self, path: Path):
        path = path.expanduser().resolve()
        path.write_text(self.to_text())

    def to_text(self):
        message = self.secret_key.buffer
        return PemEntry(self.label, message).to_text()
