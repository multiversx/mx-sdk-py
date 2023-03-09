from pathlib import Path

from multiversx_sdk_wallet.errors import ErrCannotSign
from multiversx_sdk_wallet.interfaces import ISignable, ISignature
from multiversx_sdk_wallet.user_keys import UserPublicKey, UserSecretKey
from multiversx_sdk_wallet.user_pem import UserPEM
from multiversx_sdk_wallet.user_wallet import UserWallet


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
    def from_wallet(cls, path: Path, password: str) -> 'UserSigner':
        secret_key = UserWallet.load_secret_key(path, password)
        return UserSigner(secret_key)

    def sign(self, signable: ISignable) -> ISignature:
        try:
            return self._try_sign(signable)
        except Exception as err:
            raise ErrCannotSign() from err

    def _try_sign(self, signable: ISignable) -> ISignature:
        data = signable.serialize_for_signing()
        signature = self.secret_key.sign(data)
        return signature

    def get_pubkey(self) -> UserPublicKey:
        return self.secret_key.generate_public_key()
