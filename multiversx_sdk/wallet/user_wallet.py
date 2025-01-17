import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from multiversx_sdk.wallet.crypto import EncryptedData, Randomness, decryptor, encryptor
from multiversx_sdk.wallet.interfaces import IRandomness
from multiversx_sdk.wallet.mnemonic import Mnemonic
from multiversx_sdk.wallet.user_keys import UserPublicKey, UserSecretKey


class UserWalletKind(str, Enum):
    SECRET_KEY = "secretKey"
    MNEMONIC = "mnemonic"


class UserWallet:
    def __init__(
        self,
        kind: str,
        encrypted_data: EncryptedData,
        public_key_when_kind_is_secret_key: Optional[UserPublicKey] = None,
    ) -> None:
        """
        Do not use this constructor directly. Use the static methods from_secret_key() and from_mnemonic() instead.
        """
        self.kind = kind
        self.encrypted_data = encrypted_data
        self.public_key_when_kind_is_secret_key = public_key_when_kind_is_secret_key

    @classmethod
    def from_secret_key(
        cls,
        secret_key: UserSecretKey,
        password: str,
        randomness: Union[IRandomness, None] = None,
    ) -> "UserWallet":
        randomness = randomness or Randomness()

        public_key = secret_key.generate_public_key()
        data = secret_key.buffer + public_key.buffer
        encrypted_data = encryptor.encrypt(data, password, randomness)

        return cls(
            kind=UserWalletKind.SECRET_KEY.value,
            encrypted_data=encrypted_data,
            public_key_when_kind_is_secret_key=public_key,
        )

    @classmethod
    def from_mnemonic(cls, mnemonic: str, password: str, randomness: Union[IRandomness, None] = None) -> "UserWallet":
        randomness = randomness or Randomness()

        Mnemonic.assert_text_is_valid(mnemonic)
        data = mnemonic.encode()
        encrypted_data = encryptor.encrypt(data, password, randomness)

        return cls(kind=UserWalletKind.MNEMONIC.value, encrypted_data=encrypted_data)

    @classmethod
    def decrypt_secret_key(cls, keyfile_object: dict[str, Any], password: str) -> UserSecretKey:
        # Here, we check the "kind" field only for files that have it. Older keystore files (holding only secret keys) do not have this field.
        kind = keyfile_object.get("kind", None)
        if kind and kind != UserWalletKind.SECRET_KEY.value:
            raise Exception(f"Expected kind to be {UserWalletKind.SECRET_KEY.value}, but it was {kind}")

        encrypted_data = EncryptedData.from_keyfile_object(keyfile_object)
        buffer = decryptor.decrypt(encrypted_data, password)
        buffer = buffer.rjust(32, b"\x00")
        seed = buffer[:32]
        return UserSecretKey(seed)

    @classmethod
    def decrypt_mnemonic(cls, keyfile_object: dict[str, Any], password: str) -> Mnemonic:
        if keyfile_object["kind"] != UserWalletKind.MNEMONIC.value:
            raise Exception(f"Expected kind to be {UserWalletKind.MNEMONIC.value}, but it was {keyfile_object['kind']}")

        encrypted_data = EncryptedData.from_keyfile_object(keyfile_object)
        buffer = decryptor.decrypt(encrypted_data, password)
        mnemonic = Mnemonic(buffer.decode())
        return mnemonic

    @classmethod
    def load_secret_key(cls, path: Path, password: str, address_index: Optional[int] = None) -> "UserSecretKey":
        """
        Loads a secret key from a keystore file.

        :param path: The path to the keystore file.
        :param password: The password to decrypt the keystore file.
        :param address_index: The index of the address to load. This is only used when the keystore file contains a mnemonic, and the secret key has to be derived from this mnemonic.
        """
        key_file_json = path.expanduser().resolve().read_text()
        key_file_object = json.loads(key_file_json)
        kind = key_file_object.get("kind", UserWalletKind.SECRET_KEY.value)
        logging.debug(f"UserWallet.load_secret_key(), kind = {kind}")

        if kind == UserWalletKind.SECRET_KEY.value:
            if address_index is not None:
                raise Exception("address_index must not be provided when kind == 'secretKey'")
            secret_key = cls.decrypt_secret_key(key_file_object, password)
        elif kind == UserWalletKind.MNEMONIC.value:
            mnemonic = cls.decrypt_mnemonic(key_file_object, password)
            secret_key = mnemonic.derive_key(address_index or 0)
        else:
            raise Exception(f"Unknown kind: {kind}")

        return secret_key

    def save(self, path: Path, address_hrp: Optional[str] = None):
        path = path.expanduser().resolve()
        json_content = self.to_json(address_hrp)
        path.write_text(json_content)

    def to_json(self, address_hrp: Optional[str] = None) -> str:
        obj = self.to_dict(address_hrp)
        return json.dumps(obj, indent=4)

    def to_dict(self, address_hrp: Optional[str] = None) -> dict[str, Any]:
        if self.kind == UserWalletKind.SECRET_KEY.value:
            return self._to_dict_when_kind_is_secret_key(address_hrp)

        return self._to_dict_when_kind_is_mnemonic()

    def _to_dict_when_kind_is_secret_key(self, address_hrp: Optional[str] = None) -> dict[str, Any]:
        if self.public_key_when_kind_is_secret_key is None:
            raise Exception("Public key isn't available")

        crypto_section = self._get_crypto_section_as_dict()

        envelope = {
            "version": self.encrypted_data.version,
            "kind": self.kind,
            "id": self.encrypted_data.id,
            "address": self.public_key_when_kind_is_secret_key.hex(),
            "bech32": self.public_key_when_kind_is_secret_key.to_address(address_hrp).to_bech32(),
            "crypto": crypto_section,
        }

        return envelope

    def _to_dict_when_kind_is_mnemonic(self) -> dict[str, Any]:
        crypto_section = self._get_crypto_section_as_dict()

        envelope = {
            "version": self.encrypted_data.version,
            "kind": self.kind,
            "id": self.encrypted_data.id,
            "crypto": crypto_section,
        }

        return envelope

    def _get_crypto_section_as_dict(self) -> dict[str, Any]:
        return {
            "ciphertext": self.encrypted_data.ciphertext,
            "cipherparams": {"iv": self.encrypted_data.iv},
            "cipher": self.encrypted_data.cipher,
            "kdf": self.encrypted_data.kdf,
            "kdfparams": {
                "dklen": self.encrypted_data.kdfparams.dklen,
                "salt": self.encrypted_data.salt,
                "n": self.encrypted_data.kdfparams.n,
                "r": self.encrypted_data.kdfparams.r,
                "p": self.encrypted_data.kdfparams.p,
            },
            "mac": self.encrypted_data.mac,
        }
