from typing import Protocol

from multiversx_sdk.core.address import Address


class INetworkConfig(Protocol):
    min_gas_limit: int
    gas_per_data_byte: int
    gas_price_modifier: float


class IAccount(Protocol):
    @property
    def address(self) -> Address:
        ...

    def sign(self, data: bytes) -> bytes:
        ...
