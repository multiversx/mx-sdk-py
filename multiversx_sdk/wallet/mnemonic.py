import mnemonic

from multiversx_sdk.wallet import core
from multiversx_sdk.wallet.constants import BIP39_LANGUAGE, BIP39_STRENGTH
from multiversx_sdk.wallet.errors import InvalidMnemonicError
from multiversx_sdk.wallet.user_keys import UserSecretKey


class Mnemonic:
    def __init__(self, text: str) -> None:
        text = text.strip()
        self.assert_text_is_valid(text)
        self.text = text

    @classmethod
    def assert_text_is_valid(cls, text: str) -> None:
        if not cls.is_text_valid(text):
            raise InvalidMnemonicError()

    @classmethod
    def is_text_valid(cls, text: str) -> bool:
        return mnemonic.Mnemonic(BIP39_LANGUAGE).check(text)

    @classmethod
    def generate(cls) -> "Mnemonic":
        text = mnemonic.Mnemonic(BIP39_LANGUAGE).generate(strength=BIP39_STRENGTH)
        return cls(text)

    @classmethod
    def from_entropy(cls, entropy: bytes) -> "Mnemonic":
        text = mnemonic.Mnemonic(BIP39_LANGUAGE).to_mnemonic(entropy)
        return cls(text)

    def derive_key(self, address_index: int = 0) -> UserSecretKey:
        secret_key = core.derive_keys(self.text, address_index)
        return UserSecretKey(secret_key)

    def get_text(self) -> str:
        return self.text

    def get_words(self) -> list[str]:
        return self.text.split()

    def get_entropy(self) -> bytes:
        entropy = mnemonic.Mnemonic(BIP39_LANGUAGE).to_entropy(self.text)
        return bytes(entropy)

    def __str__(self) -> str:
        return Mnemonic.__name__

    def __repr__(self) -> str:
        return Mnemonic.__name__
