from pathlib import Path
from typing import List

from multiversx_sdk.wallet.errors import ErrCannotSign
from multiversx_sdk.wallet.interfaces import ISignature
from multiversx_sdk.wallet.user_keys import UserPublicKey, UserSecretKey
from multiversx_sdk.wallet.user_pem import UserPEM
from multiversx_sdk.wallet.user_wallet import UserWallet


class UserSigner:
    """
    ed25519 signer
    """

    def __init__(self, secret_key: UserSecretKey) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, path: Path, index: int = 0) -> 'UserSigner':
        secret_key = UserPEM.from_file(path, index).secret_key
        return UserSigner(secret_key)

    @classmethod
    def from_pem_file_all(cls, path: Path) -> List['UserSigner']:
        users = UserPEM.from_file_all(path)
        return [UserSigner(user.secret_key) for user in users]

    @classmethod
    def from_wallet(cls, path: Path, password: str) -> 'UserSigner':
        secret_key = UserWallet.load_secret_key(path, password)
        return UserSigner(secret_key)

    def sign(self, data: bytes) -> ISignature:
        try:
            return self._try_sign(data)
        except Exception as err:
            raise ErrCannotSign() from err

    def _try_sign(self, data: bytes) -> ISignature:
        signature = self.secret_key.sign(data)
        return signature

    def get_pubkey(self) -> UserPublicKey:
        return self.secret_key.generate_public_key()
