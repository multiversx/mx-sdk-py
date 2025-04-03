from pathlib import Path

from multiversx_sdk.wallet.constants import USER_SEED_LENGTH
from multiversx_sdk.wallet.pem_entry import PemEntry
from multiversx_sdk.wallet.user_keys import UserSecretKey


class UserPEM:
    def __init__(self, label: str, secret_key: UserSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> "UserPEM":
        return cls.from_file_all(path)[index]

    @classmethod
    def from_file_all(cls, path: Path) -> list["UserPEM"]:
        text = path.expanduser().resolve().read_text()
        return cls.from_text_all(text)

    @classmethod
    def from_text(cls, text: str, index: int = 0) -> "UserPEM":
        items = cls.from_text_all(text)
        return items[index]

    @classmethod
    def from_text_all(cls, text: str) -> list["UserPEM"]:
        entries = PemEntry.from_text_all(text)
        result_items: list[UserPEM] = []

        for entry in entries:
            secret_key = UserSecretKey(entry.message[0:USER_SEED_LENGTH])
            item = cls(entry.label, secret_key)
            result_items.append(item)

        return result_items

    def save(self, path: Path):
        path = path.expanduser().resolve()
        path.write_text(self.to_text())

    def to_text(self) -> str:
        message = self.secret_key.buffer + self.public_key.buffer
        return PemEntry(self.label, message).to_text()
