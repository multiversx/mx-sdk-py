from multiversx_sdk.wallet.user_wallet import UserWallet
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.mnemonic import Mnemonic
from multiversx_sdk.core.constants import DEFAULT_HRP
from pathlib import Path


class AccountNonceHolder():
    """An abstraction representing an account's nonce on the Network."""

    def __init__(self, initial_nonce: int = 0):
        """Creates an acount nonce holder object from an initial nonce.

        Args:
            initial_nonce (int): the current nonce of the account"""
        self.nonce = initial_nonce

    def get_nonce_then_increment(self) -> int:
        """Returns the current nonce then increments it

        Returns:
            int: the current nonce"""
        nonce = self.nonce
        self.increment_nonce()
        return nonce

    def increment_nonce(self):
        """Increments the current nonce"""
        self.nonce += 1


class Account:
    def __init__(self, signer: UserSigner, hrp: str = DEFAULT_HRP) -> None:
        self.signer = signer
        self.address = signer.get_pubkey().to_address(hrp)
        self.nonce = 0

    @classmethod
    def new_from_pem(cls, file_path: Path, index: int = 0, hrp: str = DEFAULT_HRP) -> "Account":
        signer = UserSigner.from_pem_file(file_path, index)
        return Account(signer, hrp)

    @classmethod
    def new_from_keystore(cls,
                          file_path: Path,
                          password: str,
                          address_index: int = 0,
                          hrp: str = DEFAULT_HRP) -> "Account":
        secret_key = UserWallet.load_secret_key(
            file_path, password, address_index)
        signer = UserSigner(secret_key)
        return Account(signer, hrp)

    @classmethod
    def new_from_mnemonic(cls,
                          mnemonic: str,
                          address_index: int = 0,
                          hrp: str = DEFAULT_HRP) -> "Account":
        mnemonic_handler = Mnemonic(mnemonic)
        secret_key = mnemonic_handler.derive_key(address_index)
        return Account(UserSigner(secret_key), hrp)

    def sign(self, data: bytes) -> bytes:
        return self.signer.sign(data)

    def get_nonce_then_increment(self) -> int:
        nonce = self.nonce
        self.nonce += 1
        return nonce
