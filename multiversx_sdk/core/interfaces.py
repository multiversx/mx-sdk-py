from typing import Protocol

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction


class INetworkConfig(Protocol):
    min_gas_limit: int
    gas_per_data_byte: int
    gas_price_modifier: float


# fmt: off
class IAccount(Protocol):
    @property
    def use_hash_signing(self) -> bool:
        ...

    @property
    def address(self) -> Address:
        ...

    def sign_transaction(self, transaction: Transaction) -> bytes:
        ...
# fmt: on
