from multiversx_sdk.wallet.user_keys import UserPublicKey, UserSecretKey


class KeyPair:
    def __init__(self, secret_key: UserSecretKey) -> None:
        self.secret_key = secret_key
        self.public_key = self.secret_key.generate_public_key()

    @staticmethod
    def generate() -> "KeyPair":
        secret_key = UserSecretKey.generate()
        return KeyPair(secret_key)

    @staticmethod
    def new_from_bytes(data: bytes) -> "KeyPair":
        secret_key = UserSecretKey(data)
        return KeyPair(secret_key)

    def sign(self, data: bytes) -> bytes:
        """Signs using the secret key of the keypair."""
        return self.secret_key.sign(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verifies using the public key of the keypair."""
        return self.public_key.verify(data, signature)

    def get_secret_key(self) -> UserSecretKey:
        return self.secret_key

    def get_public_key(self) -> UserPublicKey:
        return self.public_key
