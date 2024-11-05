from typing import Protocol


class IToken(Protocol):
    identifier: str
    nonce: int


class ITokenTransfer(Protocol):
    @property
    def token(self) -> IToken:
        ...

    amount: int


class ITokenIdentifierParts(Protocol):
    ticker: str
    random_sequence: str
    nonce: int


class INetworkConfig(Protocol):
    min_gas_limit: int
    gas_per_data_byte: int
    gas_price_modifier: float
    chain_id: str


class IValidatorPublicKey(Protocol):
    def hex(self) -> str:
        ...
