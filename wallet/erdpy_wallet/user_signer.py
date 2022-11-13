from pathlib import Path

from nacl.signing import SigningKey

from erdpy_wallet import pem
from erdpy_wallet.errors import ErrCannotSign
from erdpy_wallet.interfaces import ISignable, ISignature


class UserSigner:
    """
    ed25519 signer
    """

    def __init__(self, secret_key: bytes) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, file: Path, index: int = 0):
        secret_key, _ = pem.parse(file, index)
        return UserSigner(secret_key)

    def sign(self, signable: ISignable) -> ISignature:
        try:
            return self._try_sign(signable)
        except Exception as err:
            raise ErrCannotSign() from err

    def _try_sign(self, signable: ISignable) -> ISignature:
        data = signable.serialize_for_signing()
        signing_key = SigningKey(self.secret_key)
        signature = signing_key.sign(data)
        return signature
