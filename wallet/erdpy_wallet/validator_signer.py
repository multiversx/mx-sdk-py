from pathlib import Path

from erdpy_wallet import pem
from erdpy_wallet.errors import ErrCannotSign
from erdpy_wallet.interfaces import ISignable, ISignature
from erdpy_wallet.validator_keys import ValidatorSecretKey


class ValidatorSigner:
    """
    Validator signer (BLS signer)
    """

    def __init__(self, secret_key: ValidatorSecretKey) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, path: Path, index: int = 0) -> 'ValidatorSigner':
        entry = pem.parse(path, index)
        secret_key = ValidatorSecretKey(entry.message)
        return ValidatorSigner(secret_key)

    def sign(self, signable: ISignable) -> ISignature:
        try:
            return self._try_sign(signable)
        except Exception as err:
            raise ErrCannotSign() from err

    def _try_sign(self, signable: ISignable) -> ISignature:
        data = signable.serialize_for_signing()
        signature = self.secret_key.sign(data)
        return signature
