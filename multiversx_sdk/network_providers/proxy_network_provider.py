import urllib.parse
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from threading import Thread
from typing import Any, Callable, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.constants import ESDT_CONTRACT_ADDRESS_HEX, METACHAIN_ID
from multiversx_sdk.core.tokens import Token
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transaction_status import TransactionStatus
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
    account_from_proxy_response,
    account_storage_entry_from_response,
    account_storage_from_response,
    block_from_response,
    definition_of_fungible_token_from_query_response,
    definition_of_tokens_collection_from_query_response,
    network_config_from_response,
    network_status_from_response,
    smart_contract_query_to_vm_query_request,
    token_amount_on_network_from_proxy_response,
    token_amounts_from_proxy_response,
    transaction_cost_estimation_from_response,
    transaction_from_proxy_response,
    transaction_from_simulate_response,
    transactions_from_send_multiple_response,
    vm_query_response_to_smart_contract_query_response,
)
from multiversx_sdk.network_providers.interface import INetworkProvider
from multiversx_sdk.network_providers.resources import (
    AccountOnNetwork,
    AccountStorage,
    AccountStorageEntry,
    AwaitingOptions,
    BlockOnNetwork,
    FungibleTokenMetadata,
    GenericResponse,
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


class ProxyNetworkProvider(INetworkProvider):
    def __init__(
        self,
        url: str,
        address_hrp: Optional[str] = None,
        config: Optional[NetworkProviderConfig] = None,
    ) -> None:
        self.url = url
        self.address_hrp = address_hrp or LibraryConfig.default_address_hrp
        self.config = config if config is not None else NetworkProviderConfig()

        self.user_agent_prefix = f"{BASE_USER_AGENT}/proxy"
        extend_user_agent(self.user_agent_prefix, self.config)

    def get_network_config(self) -> NetworkConfig:
        """Fetches the general configuration of the network."""
        response = self.do_get_generic("network/config")
        return network_config_from_response(response.get("config", {}))

    def get_network_status(self, shard: int = METACHAIN_ID) -> NetworkStatus:
        """Fetches the current status of the network."""
        response = self.do_get_generic(f"network/status/{shard}")
        return network_status_from_response(response.get("status", ""))

    def get_block(
        self,
        shard: int,
        block_hash: Optional[Union[str, bytes]] = None,
        block_nonce: Optional[int] = None,
    ) -> BlockOnNetwork:
        """Fetches a block by nonce or by hash."""
        if block_hash:
            block_hash = block_hash.hex() if isinstance(block_hash, bytes) else block_hash
            response = self.do_get_generic(f"block/{shard}/by-hash/{block_hash}")
        elif block_nonce:
            response = self.do_get_generic(f"block/{shard}/by-nonce/{block_nonce}")
        else:
            raise Exception("Block hash or block nonce not provided.")

        return block_from_response(response.get("block", {}))

    def get_latest_block(self, shard: int = METACHAIN_ID) -> BlockOnNetwork:
        """Fetches the latest block of a shard."""
        block_nonce = self.get_network_status(shard).block_nonce
        response = self.do_get_generic(f"block/{shard}/by-nonce/{block_nonce}")
        return block_from_response(response.get("block", {}))

    def get_account(self, address: Address) -> AccountOnNetwork:
        """Fetches account information for a given address."""
        data: dict[str, bool] = {}

        get_guardian_data_thread = Thread(target=self._get_guardian_data, args=(address, data))
        get_guardian_data_thread.start()

        response = self.do_get_generic(f"address/{address.to_bech32()}")
        account = account_from_proxy_response(response.to_dictionary())

        get_guardian_data_thread.join(timeout=2)
        account.is_guarded = data.get("is_guarded", False)

        return account

    def _get_guardian_data(self, address: Address, return_data: dict[str, bool]):
        guardian_data = self.do_get_generic(f"address/{address.to_bech32()}/guardian-data")
        return_data["is_guarded"] = bool(guardian_data.get("guardianData", {}).get("guarded"))

    def get_account_storage(self, address: Address) -> AccountStorage:
        """
        Fetches the storage (key-value pairs) of an account.
        When decoding the keys, the errors are ignored. Use the raw values if needed.
        """
        response = self.do_get_generic(f"address/{address.to_bech32()}/keys")
        return account_storage_from_response(response.to_dictionary())

    def get_account_storage_entry(self, address: Address, entry_key: str) -> AccountStorageEntry:
        """Fetches a specific storage entry of an account."""
        key_as_hex = entry_key.encode().hex()
        response = self.do_get_generic(f"address/{address.to_bech32()}/key/{key_as_hex}")
        return account_storage_entry_from_response(response.to_dictionary(), entry_key)

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
        response = self.do_post_generic("transaction/send", transaction.to_dictionary())
        return bytes.fromhex(response.get("txHash", ""))

    def simulate_transaction(self, transaction: Transaction, check_signature: bool = False) -> TransactionOnNetwork:
        """Simulates a transaction."""
        url = "transaction/simulate?checkSignature=false"

        if check_signature:
            url = "transaction/simulate"

        response = self.do_post_generic(url, transaction.to_dictionary())
        return transaction_from_simulate_response(transaction, response.to_dictionary().get("result", {}))

    def estimate_transaction_cost(self, transaction: Transaction) -> TransactionCostResponse:
        """Estimates the cost of a transaction."""
        response = self.do_post_generic("transaction/cost", transaction.to_dictionary())
        return transaction_cost_estimation_from_response(response.to_dictionary())

    def send_transactions(self, transactions: list[Transaction]) -> tuple[int, list[bytes]]:
        """
        Broadcasts multiple transactions and returns a tuple of (number of accepted transactions, list of transaction hashes).
        In the returned list, the order of transaction hashes corresponds to the order of transactions in the input list.
        If a transaction is not accepted, its hash is empty in the returned list.
        """
        transactions_as_dictionaries = [transaction.to_dictionary() for transaction in transactions]
        response = self.do_post_generic("transaction/send-multiple", transactions_as_dictionaries)
        return transactions_from_send_multiple_response(response.to_dictionary(), len(transactions))

    def get_transaction(self, transaction_hash: Union[bytes, str]) -> TransactionOnNetwork:
        """Fetches a transaction that was previously broadcasted (maybe already processed by the network)."""
        transaction_hash = convert_tx_hash_to_string(transaction_hash)

        def get_tx() -> dict[str, Any]:
            url = f"transaction/{transaction_hash}?withResults=true"
            return self.do_get_generic(url).get("transaction", "")

        status_task = None
        with ThreadPoolExecutor(max_workers=2) as executor:
            try:
                status_task = executor.submit(self.get_transaction_status, transaction_hash)
                tx_task = executor.submit(get_tx)

                process_status = status_task.result(timeout=5)
                tx = tx_task.result(timeout=5)

            except TimeoutError:
                raise TimeoutError("Fetching transaction or process status timed out")
            except NetworkProviderError as ge:
                raise TransactionFetchingError(ge.url, ge.data)

        return transaction_from_proxy_response(transaction_hash, tx, process_status)

    def await_transaction_completed(
        self,
        transaction_hash: Union[bytes, str],
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
        if token.nonce == 0:
            response = self.do_get_generic(f"address/{address.to_bech32()}/esdt/{token.identifier}")
        else:
            response = self.do_get_generic(f"address/{address.to_bech32()}/nft/{token.identifier}/nonce/{token.nonce}")

        return token_amount_on_network_from_proxy_response(response.to_dictionary())

    def get_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]:
        """
        Fetches the balances of an account, for all fungible tokens held by the account.
        Pagination isn't explicitly handled by a basic network provider, but can be achieved by using `do_get_generic`.
        """
        response = self.do_get_generic(f"address/{address.to_bech32()}/esdt")
        all_tokens = token_amounts_from_proxy_response(response.to_dictionary())

        return [token for token in all_tokens if token.token.nonce == 0]

    def get_non_fungible_tokens_of_account(self, address: Address) -> list[TokenAmountOnNetwork]:
        """
        Fetches the balances of an account, for all non-fungible tokens held by the account.
        Pagination isn't explicitly handled by a basic network provider, but can be achieved by using `do_get_generic`.
        """
        response = self.do_get_generic(f"address/{address.to_bech32()}/esdt")
        all_tokens = token_amounts_from_proxy_response(response.to_dictionary())

        return [token for token in all_tokens if token.token.nonce > 0]

    def get_definition_of_fungible_token(self, token_identifier: str) -> FungibleTokenMetadata:
        """Fetches the definition of a fungible token."""
        encoded_identifier = token_identifier.encode()
        query = SmartContractQuery(
            contract=Address.new_from_hex(ESDT_CONTRACT_ADDRESS_HEX, self.address_hrp),
            function="getTokenProperties",
            arguments=[encoded_identifier],
        )
        query_response = self.query_contract(query)

        return definition_of_fungible_token_from_query_response(
            query_response.return_data_parts, token_identifier, self.address_hrp
        )

    def get_definition_of_tokens_collection(self, collection_name: str) -> TokensCollectionMetadata:
        """Fetches the definition of a tokens collection."""
        encoded_identifier = collection_name.encode()
        query = SmartContractQuery(
            contract=Address.new_from_hex(ESDT_CONTRACT_ADDRESS_HEX, self.address_hrp),
            function="getTokenProperties",
            arguments=[encoded_identifier],
        )
        query_response = self.query_contract(query)

        return definition_of_tokens_collection_from_query_response(
            query_response.return_data_parts, collection_name, self.address_hrp
        )

    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        """Queries a smart contract."""
        request = smart_contract_query_to_vm_query_request(query)
        response = self.do_post_generic("vm-values/query", request)
        response = response.get("data", "")

        return vm_query_response_to_smart_contract_query_response(response, query.function)

    def get_transaction_status(self, transaction_hash: Union[str, bytes]) -> TransactionStatus:
        """Fetches the status of a transaction."""
        transaction_hash = convert_tx_hash_to_string(transaction_hash)

        response = self.do_get_generic(f"transaction/{transaction_hash}/process-status")
        return TransactionStatus(response.get("status", ""))

    def do_get_generic(self, url: str, url_parameters: Optional[dict[str, Any]] = None) -> GenericResponse:
        """Does a generic GET request against the network (handles API enveloping)."""
        url = f"{self.url}/{url}"

        if url_parameters is not None:
            url_parameters = convert_boolean_query_params_to_lowercase(url_parameters)
            params = urllib.parse.urlencode(url_parameters)
            url = f"{url}?{params}"

        response = self._do_get(url)
        return response

    def do_post_generic(self, url: str, data: Any, url_parameters: Optional[dict[str, Any]] = None) -> GenericResponse:
        """Does a generic GET request against the network (handles API enveloping)."""
        url = f"{self.url}/{url}"

        if url_parameters is not None:
            url_parameters = convert_boolean_query_params_to_lowercase(url_parameters)
            params = urllib.parse.urlencode(url_parameters)
            url = f"{url}?{params}"

        response = self._do_post(url, data)
        return response

    def _do_get(self, url: str) -> GenericResponse:
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

    def _do_post(self, url: str, payload: Any) -> GenericResponse:
        try:
            response = requests.post(url, json=payload, **self.config.requests_options)
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

    def _get_data(self, parsed: dict[str, Any], url: str) -> GenericResponse:
        err = parsed.get("error")
        code = parsed.get("code")

        if err:
            raise NetworkProviderError(url, f"code:{code}, error: {err}")

        data: dict[str, Any] = parsed.get("data", dict())
        return GenericResponse(data)

    def _extract_error_from_response(self, response: Any):
        try:
            return response.json()
        except Exception:
            return response.text
