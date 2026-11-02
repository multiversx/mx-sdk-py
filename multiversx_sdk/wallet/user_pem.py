from pathlib import Path

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import BadAddressError, BadPubkeyLengthError
from multiversx_sdk.wallet.constants import USER_SEED_LENGTH
from multiversx_sdk.wallet.errors import InvalidPemError
from multiversx_sdk.wallet.pem_entry import PemEntry, assert_index_is_valid
from multiversx_sdk.wallet.user_keys import UserPublicKey, UserSecretKey


class UserPEM:
    def __init__(self, label: str, secret_key: UserSecretKey) -> None:
        self.label = label
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()

    @classmethod
    def from_file(cls, path: Path, index: int = 0) -> "UserPEM":
        items = cls.from_file_all(path)
        assert_index_is_valid(index, len(items))
        return items[index]

    @classmethod
    def from_file_all(cls, path: Path) -> list["UserPEM"]:
        text = path.expanduser().resolve().read_text()
        return cls.from_text_all(text)

    @classmethod
    def from_text(cls, text: str, index: int = 0) -> "UserPEM":
        items = cls.from_text_all(text)
        assert_index_is_valid(index, len(items))
        return items[index]

    @classmethod
    def from_text_all(cls, text: str) -> list["UserPEM"]:
        entries = PemEntry.from_text_all(text)
        result_items: list[UserPEM] = []

        for entry in entries:
            secret_key = UserSecretKey(entry.message[0:USER_SEED_LENGTH])
            item = cls(entry.label, secret_key)
            cls._check_identity(entry, item.public_key)
            result_items.append(item)

        return result_items

    @classmethod
    def _check_identity(cls, entry: PemEntry, public_key: UserPublicKey) -> None:
        # The message holds the secret key, optionally followed by the public key.
        embedded_public_key = entry.message[USER_SEED_LENGTH:]
        if embedded_public_key and embedded_public_key != public_key.buffer:
            raise InvalidPemError("the embedded public key does not match the secret key")

        # Generally, the label is the bech32 address of the account. Other labels (e.g. custom ones) are accepted, as before.
        # The HRP isn't checked, so that files saved with a custom HRP can be loaded, as well.
        try:
            label_public_key = Address.new_from_bech32(entry.label).get_public_key()
        except (BadAddressError, BadPubkeyLengthError):
            return

        if label_public_key != public_key.buffer:
            raise InvalidPemError("the label (address) does not match the secret key")

    def save(self, path: Path):
        path = path.expanduser().resolve()
        path.write_text(self.to_text())

    def to_text(self) -> str:
        message = self.secret_key.buffer + self.public_key.buffer
        return PemEntry(self.label, message).to_text()
