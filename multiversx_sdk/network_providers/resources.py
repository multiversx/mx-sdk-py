from dataclasses import dataclass
from typing import Any, Optional

from multiversx_sdk.core import Address, Token, TransactionStatus
from multiversx_sdk.network_providers.constants import (
    DEFAULT_TRANSACTION_AWAITING_PATIENCE_IN_MILLISECONDS,
    DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS,
    DEFAULT_TRANSACTION_AWAITING_TIMEOUT_IN_MILLISECONDS,
)


class GenericResponse:
    def __init__(self, data: Any) -> None:
        self.__dict__.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def to_dictionary(self) -> dict[str, Any]:
        return self.__dict__


@dataclass
class NetworkConfig:
    raw: dict[str, Any]
    chain_id: str
    gas_per_data_byte: int
    gas_price_modifier: float
    min_gas_limit: int
    min_gas_price: int
    extra_gas_limit_for_guarded_transactions: int
    num_shards: int
    round_duration: int
    num_rounds_per_epoch: int
    genesis_timestamp: int


@dataclass
class NetworkStatus:
    raw: dict[str, Any]
    block_timestamp: int
    block_nonce: int
    highest_final_block_nonce: int
    current_round: int
    current_epoch: int


@dataclass
class BlockOnNetwork:
    raw: dict[str, Any]
    shard: int
    nonce: int
    hash: bytes
    previous_hash: bytes
    timestamp: int
    round: int
    epoch: int


@dataclass
class BlockCoordinates:
    nonce: str
    hash: bytes
    root_hash: bytes


@dataclass
class AccountOnNetwork:
    raw: dict[str, Any]
    address: Address
    nonce: int
    balance: int
    is_guarded: bool
    username: str = ""
    block_coordinates: Optional[BlockCoordinates] = None

    contract_code_hash: bytes = b""
    contract_code: bytes = b""
    contract_developer_reward: int = 0
    contract_owner_address: Optional[Address] = None
    is_contract_upgradable: bool = False
    is_contract_readable: bool = False
    is_contract_payable: bool = False
    is_contract_payable_by_contract: bool = False


@dataclass
class AccountStorageEntry:
    raw: dict[str, Any]
    key: str
    value: bytes
    block_coordinates: Optional[BlockCoordinates] = None


@dataclass
class AccountStorage:
    raw: dict[str, Any]
    entries: list[AccountStorageEntry]
    block_coordinates: Optional[BlockCoordinates] = None


@dataclass
class TransactionCostResponse:
    raw: dict[str, Any]
    gas_limit: int
    status: TransactionStatus


@dataclass
class TokenAmountOnNetwork:
    raw: dict[str, Any]
    token: Token
    amount: int
    attributes: bytes
    block_coordinates: Optional[BlockCoordinates] = None


@dataclass
class FungibleTokenMetadata:
    raw: dict[str, Any]
    identifier: str
    name: str
    ticker: str
    owner: str
    decimals: int


@dataclass
class TokensCollectionMetadata:
    raw: dict[str, Any]
    collection: str
    type: str
    name: str
    ticker: str
    owner: str
    decimals: int


@dataclass
class AwaitingOptions:
    polling_interval_in_milliseconds: int = DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS
    timeout_in_milliseconds: int = DEFAULT_TRANSACTION_AWAITING_TIMEOUT_IN_MILLISECONDS
    patience_in_milliseconds: int = DEFAULT_TRANSACTION_AWAITING_PATIENCE_IN_MILLISECONDS
