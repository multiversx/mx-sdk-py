from pathlib import Path

from erdpy_wallet import pem
from erdpy_wallet.constants import USER_SEED_LENGTH
from erdpy_wallet.errors import ErrCannotSign
from erdpy_wallet.interfaces import ISignable, ISignature
from erdpy_wallet.user_keys import UserPublicKey, UserSecretKey
from erdpy_wallet.user_wallet import UserWallet


class UserSigner:
    """
    ed25519 signer
    """

    def __init__(self, secret_key: UserSecretKey) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, path: Path, index: int = 0) -> 'UserSigner':
        entry = pem.parse(path, index)
        secret_key = UserSecretKey(entry.message[0:USER_SEED_LENGTH])
        return UserSigner(secret_key)

    @classmethod
    def from_wallet(cls, path: Path, password: str) -> 'UserSigner':
        secret_key = UserWallet.decrypt_secret_key_from_file(path, password)
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
