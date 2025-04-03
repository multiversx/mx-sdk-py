from pathlib import Path
from typing import Optional

from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.wallet.keypair import KeyPair
from multiversx_sdk.wallet.mnemonic import Mnemonic
from multiversx_sdk.wallet.user_keys import UserSecretKey
from multiversx_sdk.wallet.user_pem import UserPEM
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_wallet import UserWallet


class Account:
    def __init__(self, secret_key: UserSecretKey, hrp: Optional[str] = None) -> None:
        self.secret_key = secret_key
        self.public_key = self.secret_key.generate_public_key()
        self.address = self.public_key.to_address(hrp)
        self.nonce = 0
        self.use_hash_signing = False

    @classmethod
    def new_from_pem(cls, file_path: Path, index: int = 0, hrp: Optional[str] = None) -> "Account":
        signer = UserSigner.from_pem_file(file_path, index)
        return cls(signer.secret_key, hrp)

    @classmethod
    def new_from_keystore(
        cls,
        file_path: Path,
        password: str,
        address_index: Optional[int] = None,
        hrp: Optional[str] = None,
    ) -> "Account":
        secret_key = UserWallet.load_secret_key(file_path, password, address_index)
        return cls(secret_key, hrp)

    @classmethod
    def new_from_mnemonic(cls, mnemonic: str, address_index: int = 0, hrp: Optional[str] = None) -> "Account":
        mnemonic_handler = Mnemonic(mnemonic)
        secret_key = mnemonic_handler.derive_key(address_index)
        return cls(secret_key, hrp)

    @classmethod
    def new_from_keypair(cls, keypair: KeyPair) -> "Account":
        return cls(keypair.get_secret_key())

    def sign(self, data: bytes) -> bytes:
        """Signs using the account's secret key."""
        return self.secret_key.sign(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verifies the signature using the account's public key."""
        return self.public_key.verify(data, signature)

    def sign_transaction(self, transaction: Transaction) -> bytes:
        transaction_computer = TransactionComputer()
        serialized_tx = transaction_computer.compute_bytes_for_signing(transaction)
        return self.secret_key.sign(serialized_tx)

    def sign_message(self, message: Message) -> bytes:
        message_computer = MessageComputer()
        serialized_message = message_computer.compute_bytes_for_signing(message)
        return self.secret_key.sign(serialized_message)

    def get_nonce_then_increment(self) -> int:
        nonce = self.nonce
        self.nonce += 1
        return nonce

    def save_to_pem(self, path: Path):
        pem = UserPEM(self.address.to_bech32(), self.secret_key)
        pem.save(path)

    def save_to_keystore(self, path: Path, password: str = ""):
        """Saves the secret key to a keystore file with `kind=secretKey`."""
        wallet = UserWallet.from_secret_key(self.secret_key, password)
        wallet.save(path, self.address.get_hrp())
