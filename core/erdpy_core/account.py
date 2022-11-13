
from typing import Any

from erdpy_core.address import Address


class Account():
    def __init__(self, address: Any = None):
        self.address = Address(address)
        self.nonce: int = 0
