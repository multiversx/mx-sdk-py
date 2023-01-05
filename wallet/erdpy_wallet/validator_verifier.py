from erdpy_wallet.interfaces import IVerifiable
from erdpy_wallet.validator_keys import ValidatorPublicKey


class ValidatorVerifier:
    def __init__(self, public_key: ValidatorPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_string(cls, buffer_hex: str) -> 'ValidatorVerifier':
        public_key = ValidatorPublicKey.from_string(buffer_hex)
        return ValidatorVerifier(public_key)

    def verify(self, message: IVerifiable) -> bool:
        data = message.serialize_for_signing()
        return self.public_key.verify(data, message.signature)
