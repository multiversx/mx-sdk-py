from pathlib import Path

from multiversx_sdk.core.constants import DEFAULT_HRP
from multiversx_sdk.wallet.mnemonic import Mnemonic
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_wallet import UserWallet


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
