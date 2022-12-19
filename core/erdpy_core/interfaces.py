
from typing import Protocol


class IAddress(Protocol):
    def bech32(self) -> str: ...


INonce = int
IGasPrice = int
IGasLimit = int
IChainID = str
ITransactionVersion = int
ITransactionOptions = int
ISignature = bytes
ITokenIdentifier = str


class ITokenPayment(Protocol):
    token_identifier: str
    token_nonce: INonce
    amount_as_integer: int


class ITransactionValue(Protocol):
    def __str__(self) -> str: ...


class ITransactionPayload(Protocol):
    def encoded(self) -> str: ...


class ICodeMetadata(Protocol):
    def serialize(self) -> bytes: ...


class ITransactionBuildersConfiguration(Protocol):
    gas_price: IGasPrice
    gas_limit_esdt_issue: IGasLimit
    gas_limit_esdt_local_mint: IGasLimit
    gas_limit_esdt_local_burn: IGasLimit
    gas_limit_set_special_role: IGasLimit
    gas_limit_pausing: IGasLimit
    gas_limit_freezing: IGasLimit
    issue_cost: ITransactionValue
    transaction_version: ITransactionVersion
    transaction_options: ITransactionOptions
    deployment_address: IAddress
    esdt_contract_address: IAddress
