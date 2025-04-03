from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class ValidatorVerifier:
    def __init__(self, public_key: ValidatorPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_string(cls, buffer_hex: str) -> "ValidatorVerifier":
        public_key = ValidatorPublicKey.from_string(buffer_hex)
        return cls(public_key)

    def verify(self, data: bytes, signature: bytes) -> bool:
        return self.public_key.verify(data, signature)
