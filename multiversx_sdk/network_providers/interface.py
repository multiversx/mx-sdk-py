from typing import Any, Callable, Optional, Protocol, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import METACHAIN_ID
from multiversx_sdk.core.tokens import Token
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.network_providers.resources import (
    AccountOnNetwork,
    AccountStorage,
    AccountStorageEntry,
    AwaitingOptions,
    FungibleTokenMetadata,
    NetworkConfig,
    NetworkStatus,
    TokenAmountOnNetwork,
    TokensCollectionMetadata,
    TransactionCostResponse,
)
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
)


class INetworkProvider(Protocol):
    def get_network_config(self) -> NetworkConfig: ...

    def get_network_status(self, shard: int = METACHAIN_ID) -> NetworkStatus: ...

    def get_account(self, address: Address) -> AccountOnNetwork: ...

    def get_account_storage(self, address: Address) -> AccountStorage: ...

    def get_account_storage_entry(self, address: Address, entry_key: str) -> AccountStorageEntry: ...

    def await_account_on_condition(
        self,
        address: Address,
        condition: Callable[[AccountOnNetwork], bool],
        options: Optional[AwaitingOptions] = None,
    ) -> AccountOnNetwork: ...

    def send_transaction(self, transaction: Transaction) -> bytes: ...

    def simulate_transaction(self, transaction: Transaction) -> TransactionOnNetwork: ...

    def estimate_transaction_cost(self, transaction: Transaction) -> TransactionCostResponse: ...

    def send_transactions(self, transactions: list[Transaction]) -> tuple[int, list[bytes]]: ...

    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork: ...

    def await_transaction_completed(
        self, transaction_hash: Union[bytes, str], options: Optional[AwaitingOptions] = None
    ) -> TransactionOnNetwork: ...

    def await_transaction_on_condition(
        self,
        transaction_hash: Union[bytes, str],
        condition: Callable[[TransactionOnNetwork], bool],
        options: Optional[AwaitingOptions] = None,
    ) -> TransactionOnNetwork: ...

    def get_token_of_account(self, address: Address, token: Token) -> TokenAmountOnNetwork: ...

    def get_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]: ...

    def get_non_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]: ...

    def get_definition_of_fungible_token(self, token_identifier: str) -> FungibleTokenMetadata: ...

    def get_definition_of_tokens_collection(self, collection_name: str) -> TokensCollectionMetadata: ...

    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse: ...

    def do_get_generic(self, url: str, url_parameters: Optional[dict[str, Any]]) -> Any: ...

    def do_post_generic(self, url: str, data: Any, url_parameters: Optional[dict[str, Any]]) -> Any: ...
