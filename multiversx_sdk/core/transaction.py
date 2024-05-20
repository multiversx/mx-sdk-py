from typing import Optional, Sequence

from multiversx_sdk.core.constants import (TRANSACTION_MIN_GAS_PRICE,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from multiversx_sdk.core.interfaces import ITransaction


class Transaction:
    def __init__(self,
                 sender: str,
                 receiver: str,
                 gas_limit: int,
                 chain_id: str,
                 nonce: Optional[int] = None,
                 value: Optional[int] = None,
                 sender_username: Optional[str] = None,
                 receiver_username: Optional[str] = None,
                 gas_price: Optional[int] = None,
                 data: Optional[bytes] = None,
                 version: Optional[int] = None,
                 options: Optional[int] = None,
                 guardian: Optional[str] = None,
                 signature: Optional[bytes] = None,
                 guardian_signature: Optional[bytes] = None,
                 relayer: Optional[str] = None,
                 inner_transactions: Optional[Sequence[ITransaction]] = None) -> None:
        self.chain_id = chain_id
        self.sender = sender
        self.receiver = receiver
        self.gas_limit = gas_limit

        self.nonce = nonce or 0
        self.value = value or 0
        self.data = data or bytes()
        self.signature = signature or bytes()

        self.sender_username = sender_username or ""
        self.receiver_username = receiver_username or ""

        self.gas_price = gas_price or TRANSACTION_MIN_GAS_PRICE
        self.version = version or TRANSACTION_VERSION_DEFAULT
        self.options = options or TRANSACTION_OPTIONS_DEFAULT

        self.guardian = guardian or ""
        self.guardian_signature = guardian_signature or bytes()
        self.relayer = relayer or ""
        self.inner_transactions = inner_transactions or []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__
