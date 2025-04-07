from multiversx_sdk.core.address import Address
from multiversx_sdk.wallet.user_keys import UserPublicKey


class UserVerifier:
    def __init__(self, public_key: UserPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_address(cls, address: Address) -> "UserVerifier":
        buffer: bytes = address.get_public_key()
        public_key = UserPublicKey(buffer)
        return cls(public_key)

    def verify(self, data: bytes, signature: bytes) -> bool:
        return self.public_key.verify(data, signature)
