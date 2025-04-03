from pathlib import Path

from multiversx_sdk.wallet.errors import CannotSignError
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
    def from_pem_file(cls, path: Path, index: int = 0) -> "UserSigner":
        secret_key = UserPEM.from_file(path, index).secret_key
        return cls(secret_key)

    @classmethod
    def from_pem_file_all(cls, path: Path) -> list["UserSigner"]:
        users = UserPEM.from_file_all(path)
        return [cls(user.secret_key) for user in users]

    @classmethod
    def from_wallet(cls, path: Path, password: str) -> "UserSigner":
        secret_key = UserWallet.load_secret_key(path, password)
        return cls(secret_key)

    def sign(self, data: bytes) -> bytes:
        try:
            return self._try_sign(data)
        except Exception as err:
            raise CannotSignError() from err

    def _try_sign(self, data: bytes) -> bytes:
        signature = self.secret_key.sign(data)
        return signature

    def get_pubkey(self) -> UserPublicKey:
        return self.secret_key.generate_public_key()
