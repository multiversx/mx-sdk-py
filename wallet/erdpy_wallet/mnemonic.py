import mnemonic

from erdpy_wallet import core
from erdpy_wallet.constants import BIP39_LANGUAGE, BIP39_STRENGTH
from erdpy_wallet.errors import ErrBadMnemonic
from erdpy_wallet.user_keys import UserSecretKey


class Mnemonic:
    def __init__(self, text: str) -> None:
        ok = mnemonic.Mnemonic(BIP39_LANGUAGE).check(text)
        if not ok:
            raise ErrBadMnemonic()

        self.text = text

    @classmethod
    def generate(cls) -> 'Mnemonic':
        text = mnemonic.Mnemonic(BIP39_LANGUAGE).generate(strength=BIP39_STRENGTH)
        return Mnemonic(text)

    def derive_key(self, address_index: int = 0) -> UserSecretKey:
        secret_key = core.derive_keys(self.text, address_index)
        return UserSecretKey(secret_key)

    def get_text(self):
        return self.text

    def get_words(self):
        return self.text.split()

    def __str__(self) -> str:
        return Mnemonic.__name__

    def __repr__(self) -> str:
        return Mnemonic.__name__
