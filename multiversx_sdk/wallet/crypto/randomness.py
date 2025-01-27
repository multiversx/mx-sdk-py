import os
from typing import Optional
from uuid import uuid4

from multiversx_sdk.wallet.crypto.constants import RANDOM_IV_LENGTH, RANDOM_SALT_LENGTH


class Randomness:
    def __init__(
        self,
        salt: Optional[bytes] = None,
        iv: Optional[bytes] = None,
        id: Optional[str] = None,
    ):
        self.salt = salt or os.urandom(RANDOM_SALT_LENGTH)
        self.iv = iv or os.urandom(RANDOM_IV_LENGTH)
        self.id = id or str(uuid4())
