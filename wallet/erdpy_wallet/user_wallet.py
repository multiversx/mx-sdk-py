import json
from pathlib import Path
from typing import Any, Dict, Union

from erdpy_wallet import keyfile
from erdpy_wallet.interfaces import IUserWalletRandomness
from erdpy_wallet.user_keys import UserSecretKey


class UserWallet:
    def __init__(self, secret_key: UserSecretKey, password: str, randomness: Union[IUserWalletRandomness, None] = None) -> None:
        self.secret_key = secret_key
        self.public_key = secret_key.generate_public_key()
        self.password = password
        self.randomness = randomness

    @classmethod
    def decrypt_secret_key_from_file(cls, path: Path, password: str) -> UserSecretKey:
        with open(path) as f:
            key_file_object = json.load(f)

        return cls.decrypt_secret_key(key_file_object, password)

    @classmethod
    def decrypt_secret_key(cls, keyfile_object: Any, password: str) -> UserSecretKey:
        _, buffer = keyfile.load_from_key_file_object(keyfile_object, password)
        return UserSecretKey(buffer)

    def save(self, path: Path, address_hrp: str):
        obj = self.to_keyfile_object(address_hrp)

        with open(path, 'w') as json_file:
            json.dump(obj, json_file, indent=4)

    def to_keyfile_object(self, address_hrp: str) -> Dict[str, Any]:
        return keyfile.convert_to_keyfile_object(self.secret_key.buffer, self.public_key.buffer, self.password, self.randomness, address_hrp)
