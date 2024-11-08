from typing import Protocol


class INetworkConfig(Protocol):
    min_gas_limit: int
    gas_per_data_byte: int
    gas_price_modifier: float


class IValidatorPublicKey(Protocol):
    def hex(self) -> str:
        ...
