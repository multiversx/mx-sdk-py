from pathlib import Path

from multiversx_sdk.wallet.errors import ErrCannotSign
from multiversx_sdk.wallet.interfaces import ISignature
from multiversx_sdk.wallet.validator_keys import (ValidatorPublicKey,
                                                  ValidatorSecretKey)
from multiversx_sdk.wallet.validator_pem import ValidatorPEM


class ValidatorSigner:
    """
    Validator signer (BLS signer)
    """

    def __init__(self, secret_key: ValidatorSecretKey) -> None:
        self.secret_key = secret_key

    @classmethod
    def from_pem_file(cls, path: Path, index: int = 0) -> 'ValidatorSigner':
        secret_key = ValidatorPEM.from_file(path, index).secret_key
        return ValidatorSigner(secret_key)

    def sign(self, data: bytes) -> ISignature:
        try:
            return self._try_sign(data)
        except Exception as err:
            raise ErrCannotSign() from err

    def _try_sign(self, data: bytes) -> ISignature:
        signature = self.secret_key.sign(data)
        return signature

    def get_pubkey(self) -> ValidatorPublicKey:
        return self.secret_key.generate_public_key()
