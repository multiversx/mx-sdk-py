import urllib.parse
from typing import Any, Callable, Optional, Union, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from multiversx_sdk.core import (
    Address,
    Token,
    TokenComputer,
    Transaction,
    TransactionOnNetwork,
)
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.constants import METACHAIN_ID
from multiversx_sdk.network_providers.account_awaiter import AccountAwaiter
from multiversx_sdk.network_providers.config import NetworkProviderConfig
from multiversx_sdk.network_providers.constants import (
    BASE_USER_AGENT,
    DEFAULT_ACCOUNT_AWAITING_PATIENCE_IN_MILLISECONDS,
)
from multiversx_sdk.network_providers.errors import (
    NetworkProviderError,
    TransactionFetchingError,
)
from multiversx_sdk.network_providers.http_resources import (
    account_from_api_response,
    account_storage_entry_from_response,
    account_storage_from_response,
    block_from_response,
    definition_of_fungible_token_from_api_response,
    definition_of_tokens_collection_from_api_response,
    smart_contract_query_to_vm_query_request,
    token_amount_from_api_response,
    transaction_cost_estimation_from_response,
    transaction_from_api_response,
    transaction_from_simulate_response,
    transactions_from_send_multiple_response,
    vm_query_response_to_smart_contract_query_response,
)
from multiversx_sdk.network_providers.interface import INetworkProvider
from multiversx_sdk.network_providers.proxy_network_provider import ProxyNetworkProvider
from multiversx_sdk.network_providers.resources import (
    AccountOnNetwork,
    AccountStorage,
    AccountStorageEntry,
    AwaitingOptions,
    BlockOnNetwork,
    FungibleTokenMetadata,
    NetworkConfig,
    NetworkStatus,
    TokenAmountOnNetwork,
    TokensCollectionMetadata,
    TransactionCostResponse,
)
from multiversx_sdk.network_providers.shared import (
    convert_boolean_query_params_to_lowercase,
    convert_tx_hash_to_string,
)
from multiversx_sdk.network_providers.transaction_awaiter import TransactionAwaiter
from multiversx_sdk.network_providers.user_agent import extend_user_agent
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
)


class ApiNetworkProvider(INetworkProvider):
    def __init__(
        self,
        url: str,
        address_hrp: Optional[str] = None,
        config: Optional[NetworkProviderConfig] = None,
    ) -> None:
        self.url = url
        self.address_hrp = address_hrp or LibraryConfig.default_address_hrp
        self.backing_proxy = ProxyNetworkProvider(url, self.address_hrp)
        self.config = config if config is not None else NetworkProviderConfig()

        self.user_agent_prefix = f"{BASE_USER_AGENT}/api"
        extend_user_agent(self.user_agent_prefix, self.config)

    def get_network_config(self) -> NetworkConfig:
        """Fetches the general configuration of the network."""
        return self.backing_proxy.get_network_config()

    def get_network_status(self, shard: int = METACHAIN_ID) -> NetworkStatus:
        """Fetches the current status of the network."""
        return self.backing_proxy.get_network_status(shard)

    def get_block(self, block_hash: Union[str, bytes]) -> BlockOnNetwork:
        """Fetches a block by hash."""
        block_hash = block_hash.hex() if isinstance(block_hash, bytes) else block_hash

        result = self.do_get_generic(f"blocks/{block_hash}")
        return block_from_response(result)

    def get_latest_block(self) -> BlockOnNetwork:
        """Fetches the latest block of a shard."""
        result = self.do_get_generic("/blocks/latest")
        return block_from_response(result)

    def get_account(self, address: Address) -> AccountOnNetwork:
        """Fetches account information for a given address."""
        response = self.do_get_generic(f"accounts/{address.to_bech32()}")
        account = account_from_api_response(response)
        return account

    def get_account_storage(self, address: Address) -> AccountStorage:
        """
        Fetches the storage (key-value pairs) of an account.
        When decoding the keys, the errors are ignored. Use the raw values if needed.
        """
        response: dict[str, Any] = self.do_get_generic(f"address/{address.to_bech32()}/keys")
        return account_storage_from_response(response.get("data", {}))

    def get_account_storage_entry(self, address: Address, entry_key: str) -> AccountStorageEntry:
        """Fetches a specific storage entry of an account."""
        key_as_hex = entry_key.encode().hex()
        response: dict[str, Any] = self.do_get_generic(f"address/{address.to_bech32()}/key/{key_as_hex}")
        return account_storage_entry_from_response(response.get("data", {}), entry_key)

    def await_account_on_condition(
        self,
        address: Address,
        condition: Callable[[AccountOnNetwork], bool],
        options: Optional[AwaitingOptions] = None,
    ) -> AccountOnNetwork:
        """Waits until an account satisfies a given condition."""
        if options is None:
            options = AwaitingOptions(patience_in_milliseconds=DEFAULT_ACCOUNT_AWAITING_PATIENCE_IN_MILLISECONDS)

        awaiter = AccountAwaiter(
            fetcher=self,
            polling_interval_in_milliseconds=options.polling_interval_in_milliseconds,
            timeout_interval_in_milliseconds=options.timeout_in_milliseconds,
            patience_time_in_milliseconds=options.patience_in_milliseconds,
        )

        return awaiter.await_on_condition(address=address, condition=condition)

    def send_transaction(self, transaction: Transaction) -> bytes:
        """Broadcasts a transaction and returns its hash."""
        response = self.do_post_generic("transactions", transaction.to_dictionary())
        return bytes.fromhex(response.get("txHash", ""))

    def simulate_transaction(self, transaction: Transaction, check_signature: bool = False) -> TransactionOnNetwork:
        """Simulates a transaction."""
        url = "transaction/simulate?checkSignature=false"

        if check_signature:
            url = "transaction/simulate"

        response: dict[str, Any] = self.do_post_generic(url, transaction.to_dictionary())
        return transaction_from_simulate_response(transaction, response.get("data", {}).get("result", {}))

    def estimate_transaction_cost(self, transaction: Transaction) -> TransactionCostResponse:
        """Estimates the cost of a transaction."""
        response: dict[str, Any] = self.do_post_generic("transaction/cost", transaction.to_dictionary())
        return transaction_cost_estimation_from_response(response.get("data", {}))

    def send_transactions(self, transactions: list[Transaction]) -> tuple[int, list[bytes]]:
        """
        Broadcasts multiple transactions and returns a tuple of (number of accepted transactions, list of transaction hashes).
        In the returned list, the order of transaction hashes corresponds to the order of transactions in the input list.
        If a transaction is not accepted, its hash is empty in the returned list.
        """
        transactions_as_dictionaries = [transaction.to_dictionary() for transaction in transactions]
        response: dict[str, Any] = self.do_post_generic("transaction/send-multiple", transactions_as_dictionaries)
        return transactions_from_send_multiple_response(response.get("data", {}), len(transactions))

    def get_transaction(self, transaction_hash: Union[str, bytes]) -> TransactionOnNetwork:
        """Fetches a transaction that was previously broadcasted (maybe already processed by the network)."""
        transaction_hash = convert_tx_hash_to_string(transaction_hash)
        try:
            response = self.do_get_generic(f"transactions/{transaction_hash}")
        except NetworkProviderError as ge:
            raise TransactionFetchingError(ge.url, ge.data)
        return transaction_from_api_response(transaction_hash, response)

    def get_transactions(
        self, address: Address, url_parameters: Optional[dict[str, Any]] = None
    ) -> list[TransactionOnNetwork]:
        """Fetches the transactions of an account"""
        try:
            response = self.do_get_generic(f"accounts/{address.to_bech32()}/transactions", url_parameters)
        except NetworkProviderError as ge:
            raise TransactionFetchingError(ge.url, ge.data)

        transactions: list[TransactionOnNetwork] = []
        for tx in response:
            hash = tx.get("txHash")
            transactions.append(transaction_from_api_response(hash, tx))

        return transactions

    def await_transaction_completed(
        self,
        transaction_hash: Union[str, bytes],
        options: Optional[AwaitingOptions] = None,
    ) -> TransactionOnNetwork:
        """Waits until the transaction is completely processed."""
        transaction_hash = convert_tx_hash_to_string(transaction_hash)

        if options is None:
            options = AwaitingOptions()

        awaiter = TransactionAwaiter(
            fetcher=self,
            polling_interval_in_milliseconds=options.polling_interval_in_milliseconds,
            timeout_interval_in_milliseconds=options.timeout_in_milliseconds,
            patience_time_in_milliseconds=options.patience_in_milliseconds,
        )

        return awaiter.await_completed(transaction_hash)

    def await_transaction_on_condition(
        self,
        transaction_hash: Union[str, bytes],
        condition: Callable[[TransactionOnNetwork], bool],
        options: Optional[AwaitingOptions] = None,
    ) -> TransactionOnNetwork:
        """Waits until a transaction satisfies a given condition."""
        transaction_hash = convert_tx_hash_to_string(transaction_hash)

        if options is None:
            options = AwaitingOptions()

        awaiter = TransactionAwaiter(
            fetcher=self,
            polling_interval_in_milliseconds=options.polling_interval_in_milliseconds,
            timeout_interval_in_milliseconds=options.timeout_in_milliseconds,
            patience_time_in_milliseconds=options.patience_in_milliseconds,
        )

        return awaiter.await_on_condition(transaction_hash, condition)

    def get_token_of_account(self, address: Address, token: Token) -> TokenAmountOnNetwork:
        """
        Fetches the balance of an account, for a given token.
        Able to handle both fungible and non-fungible tokens (NFTs, SFTs, MetaESDTs).
        """
        if token.nonce:
            identifier = TokenComputer().compute_extended_identifier(token)
            result = self.do_get_generic(f"accounts/{address.to_bech32()}/nfts/{identifier}")
        else:
            result = self.do_get_generic(f"accounts/{address.to_bech32()}/tokens/{token.identifier}")

        return token_amount_from_api_response(result)

    def get_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]:
        """
        Fetches the balances of an account, for all fungible tokens held by the account.
        Pagination isn't explicitly handled by a basic network provider, but can be achieved by using `do_get_generic`.
        """
        result: list[dict[str, Any]] = self.do_get_generic(f"accounts/{address.to_bech32()}/tokens")
        return [token_amount_from_api_response(token) for token in result]

    def get_non_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]:
        """
        Fetches the balances of an account, for all non-fungible tokens held by the account.
        Pagination isn't explicitly handled by a basic network provider, but can be achieved by using `do_get_generic`.
        """
        result: list[dict[str, Any]] = self.do_get_generic(f"accounts/{address.to_bech32()}/nfts")
        return [token_amount_from_api_response(token) for token in result]

    def get_definition_of_fungible_token(self, token_identifier: str) -> FungibleTokenMetadata:
        """Fetches the definition of a fungible token."""
        result = self.do_get_generic(f"tokens/{token_identifier}")
        return definition_of_fungible_token_from_api_response(result)

    def get_definition_of_tokens_collection(self, collection_name: str) -> TokensCollectionMetadata:
        """Fetches the definition of a tokens collection."""
        result = self.do_get_generic(f"collections/{collection_name}")
        return definition_of_tokens_collection_from_api_response(result)

    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        request = smart_contract_query_to_vm_query_request(query)
        response = self.do_post_generic("query", request)
        return vm_query_response_to_smart_contract_query_response(response, query.function)

    def do_get_generic(self, url: str, url_parameters: Optional[dict[str, Any]] = None) -> Any:
        """Does a generic GET request against the network(handles API enveloping)."""
        url = f"{self.url}/{url}"

        if url_parameters is not None:
            url_parameters = convert_boolean_query_params_to_lowercase(url_parameters)
            params = urllib.parse.urlencode(url_parameters)
            url = f"{url}?{params}"

        response = self._do_get(url)
        return response

    def do_post_generic(self, url: str, data: Any, url_parameters: Optional[dict[str, Any]] = None) -> Any:
        """Does a generic GET request against the network(handles API enveloping)."""
        url = f"{self.url}/{url}"

        if url_parameters is not None:
            url_parameters = convert_boolean_query_params_to_lowercase(url_parameters)
            params = urllib.parse.urlencode(url_parameters)
            url = f"{url}?{params}"

        response = self._do_post(url, data)
        return response

    def _do_get(self, url: str) -> Any:
        try:
            retry_strategy = Retry(
                total=self.config.requests_retry_options.retries,
                backoff_factor=self.config.requests_retry_options.backoff_factor,
                status_forcelist=self.config.requests_retry_options.status_forcelist,
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)

            with requests.Session() as session:
                session.mount("https://", adapter)
                session.mount("http://", adapter)
                response = session.get(url, **self.config.requests_options)

            response.raise_for_status()
            parsed = response.json()
            return self._get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise NetworkProviderError(url, error_data)
        except requests.ConnectionError as err:
            raise NetworkProviderError(url, err)
        except Exception as err:
            raise NetworkProviderError(url, err)

    def _do_post(self, url: str, payload: Any) -> dict[str, Any]:
        try:
            response = requests.post(url, json=payload, **self.config.requests_options)
            response.raise_for_status()
            parsed = response.json()
            return cast(dict[str, Any], self._get_data(parsed, url))
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise NetworkProviderError(url, error_data)
        except requests.ConnectionError as err:
            raise NetworkProviderError(url, err)
        except Exception as err:
            raise NetworkProviderError(url, err)

    def _get_data(self, parsed: Any, url: str) -> Any:
        if isinstance(parsed, list):
            return cast(Any, parsed)
        else:
            err = parsed.get("error", None)
            if err:
                code = parsed.get("statusCode")
                raise NetworkProviderError(url, f"code:{code}, error: {err}")
            else:
                return parsed

    def _extract_error_from_response(self, response: Any):
        try:
            return response.json()
        except Exception:
            return response.text
