from multiversx_sdk_wallet.interfaces import ISignature
from multiversx_sdk_wallet.validator_keys import ValidatorPublicKey


class ValidatorVerifier:
    def __init__(self, public_key: ValidatorPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_string(cls, buffer_hex: str) -> 'ValidatorVerifier':
        public_key = ValidatorPublicKey.from_string(buffer_hex)
        return ValidatorVerifier(public_key)

    def verify(self, data: bytes, signature: ISignature) -> bool:
        return self.public_key.verify(data, signature)
