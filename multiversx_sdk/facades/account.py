from pathlib import Path
from typing import Optional

from multiversx_sdk.wallet.mnemonic import Mnemonic
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_wallet import UserWallet

DEFAULT_HRP = "erd"


class Account:
    def __init__(self, signer: UserSigner, hrp: Optional[str] = None) -> None:
        self.signer = signer
        hrp = hrp if hrp else DEFAULT_HRP
        self.address = signer.get_pubkey().to_address(hrp)
        self.nonce = 0

    @classmethod
    def new_from_pem(cls, file_path: Path, index: Optional[int] = None, hrp: Optional[str] = None) -> "Account":
        account_index = index if index else 0
        signer = UserSigner.from_pem_file(file_path, account_index)
        return Account(signer, hrp)

    @classmethod
    def new_from_keystore(cls,
                          file_path: Path,
                          password: str,
                          address_index: Optional[int] = None,
                          hrp: Optional[str] = None) -> "Account":
        secret_key = UserWallet.load_secret_key(file_path, password, address_index)
        signer = UserSigner(secret_key)
        return Account(signer, hrp)

    @classmethod
    def new_from_mnemonic(cls,
                          mnemonic: str,
                          address_index: Optional[int] = None,
                          hrp: Optional[str] = None) -> "Account":
        index = address_index if address_index else 0

        mnemonic_object = Mnemonic(mnemonic)
        secret_key = mnemonic_object.derive_key(index)
        return Account(UserSigner(secret_key), hrp)

    def sign(self, data: bytes) -> bytes:
        return self.signer.sign(data)

    def get_nonce_then_increment(self) -> int:
        nonce = self.nonce
        self.nonce += 1
        return nonce
