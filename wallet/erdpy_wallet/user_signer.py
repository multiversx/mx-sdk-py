from pathlib import Path

from erdpy_wallet.errors import ErrCannotSign
from erdpy_wallet.interfaces import ISignable, ISignature
from erdpy_wallet.interfaces_as_output import IAddressAsOutput
from erdpy_wallet.user_keys import UserSecretKey


class UserSigner:
    """
    ed25519 signer
    """

    def __init__(self, secret_key: UserSecretKey) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, path: Path, index: int = 0) -> 'UserSigner':
        secret_key = UserSecretKey.from_pem_file(path, index)
        return UserSigner(secret_key)

    @classmethod
    def from_wallet(cls, path: Path, password: str):
        secret_key = UserSecretKey.from_wallet_file(path, password)
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

    def get_address(self) -> IAddressAsOutput:
        public_key = self.secret_key.generate_public_key()
        return public_key.to_address()
