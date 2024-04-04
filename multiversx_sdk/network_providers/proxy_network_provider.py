from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import requests
from requests.auth import AuthBase

from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.network_providers.accounts import (AccountOnNetwork,
                                                       GuardianData)
from multiversx_sdk.network_providers.constants import (DEFAULT_ADDRESS_HRP,
                                                        ESDT_CONTRACT_ADDRESS,
                                                        METACHAIN_ID)
from multiversx_sdk.network_providers.contract_query_requests import \
    ContractQueryRequest
from multiversx_sdk.network_providers.contract_query_response import \
    ContractQueryResponse
from multiversx_sdk.network_providers.errors import GenericError
from multiversx_sdk.network_providers.interface import IAddress, IContractQuery
from multiversx_sdk.network_providers.network_config import NetworkConfig
from multiversx_sdk.network_providers.network_status import NetworkStatus
from multiversx_sdk.network_providers.resources import (GenericResponse,
                                                        SimulateResponse)
from multiversx_sdk.network_providers.token_definitions import (
    DefinitionOfFungibleTokenOnNetwork, DefinitionOfTokenCollectionOnNetwork)
from multiversx_sdk.network_providers.tokens import (
    FungibleTokenOfAccountOnNetwork, NonFungibleTokenOfAccountOnNetwork)
from multiversx_sdk.network_providers.transaction_status import \
    TransactionStatus
from multiversx_sdk.network_providers.transactions import (
    ITransaction, TransactionOnNetwork)


class ProxyNetworkProvider:
    def __init__(
            self,
            url: str,
            auth: Union[AuthBase, None] = None,
            address_hrp: str = DEFAULT_ADDRESS_HRP
    ) -> None:
        self.url = url
        self.auth = auth
        self.address_hrp = address_hrp

    def get_network_config(self) -> NetworkConfig:
        response = self.do_get_generic('network/config')
        network_config = NetworkConfig.from_http_response(response.get('config', ''))
        return network_config

    def get_network_gas_configs(self) -> Dict[str, Any]:
        response = self.do_get_generic("network/gas-configs").to_dictionary()
        return response

    def get_network_status(self, shard: Optional[int] = METACHAIN_ID) -> NetworkStatus:
        response = self.do_get_generic(f'network/status/{shard}')
        network_status = NetworkStatus.from_http_response(response.get('status', ''))
        return network_status

    def get_account(self, address: IAddress) -> AccountOnNetwork:
        response = self.do_get_generic(f'address/{address.to_bech32()}')
        account = AccountOnNetwork.from_http_response(response.get('account', ''))
        return account

    def get_guardian_data(self, address: IAddress) -> GuardianData:
        response = self.do_get_generic(f'address/{address.to_bech32()}/guardian-data')
        account_guardian = GuardianData.from_http_response(response.get('guardianData', ''))
        return account_guardian

    def get_fungible_tokens_of_account(self, address: IAddress) -> List[FungibleTokenOfAccountOnNetwork]:
        url = f'address/{address.to_bech32()}/esdt'
        response = self.do_get_generic(url)
        items = response.get('esdts')
        esdts = [items[key] for key in items.keys() if items[key].get('nonce', '') == '']
        tokens = [FungibleTokenOfAccountOnNetwork.from_http_response(esdt) for esdt in esdts]
        return tokens

    def get_nonfungible_tokens_of_account(self, address: IAddress) -> List[NonFungibleTokenOfAccountOnNetwork]:
        url = f'address/{address.to_bech32()}/esdt'
        response = self.do_get_generic(url)
        items = response.get('esdts')
        nfts = [items[key] for key in items.keys() if items[key].get('nonce', -1) > 0]
        result = [NonFungibleTokenOfAccountOnNetwork.from_proxy_http_response(nft) for nft in nfts]
        return list(result)

    def get_fungible_token_of_account(self, address: IAddress, identifier: str) -> FungibleTokenOfAccountOnNetwork:
        response = self.do_get_generic(f'address/{address.to_bech32()}/esdt/{identifier}')
        token = FungibleTokenOfAccountOnNetwork.from_http_response(response.get('tokenData'))
        return token

    def get_nonfungible_token_of_account(self, address: IAddress, collection: str, nonce: int) -> NonFungibleTokenOfAccountOnNetwork:
        response = self.do_get_generic(f'address/{address.to_bech32()}/nft/{collection}/nonce/{nonce}')
        token = NonFungibleTokenOfAccountOnNetwork.from_proxy_http_response_by_nonce(response.get('tokenData', ''))
        return token

    def get_transaction(self, tx_hash: str, with_process_status: Optional[bool] = False) -> TransactionOnNetwork:
        def get_process_status() -> TransactionStatus:
            return self.get_transaction_status(tx_hash)

        def get_tx() -> Dict[str, Any]:
            url = f"transaction/{tx_hash}?withResults=true"
            return self.do_get_generic(url).get('transaction', '')

        status_task = None
        with ThreadPoolExecutor(max_workers=2) as executor:
            if with_process_status:
                status_task = executor.submit(get_process_status)

            tx_task = executor.submit(get_tx)

        process_status = status_task.result() if status_task else None
        tx = tx_task.result()
        transaction = TransactionOnNetwork.from_proxy_http_response(tx_hash, tx, process_status)

        return transaction

    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        response = self.do_get_generic(f'transaction/{tx_hash}/process-status')
        status = TransactionStatus(response.get('status', ''))
        return status

    def send_transaction(self, transaction: ITransaction) -> str:
        transactions_converter = TransactionsConverter()
        response = self.do_post_generic('transaction/send', transactions_converter.transaction_to_dictionary(transaction))
        return response.get('txHash', '')

    def send_transactions(self, transactions: Sequence[ITransaction]) -> Tuple[int, Dict[str, str]]:
        transactions_converter = TransactionsConverter()
        transactions_as_dictionaries = [transactions_converter.transaction_to_dictionary(transaction) for transaction in transactions]
        response = self.do_post_generic('transaction/send-multiple', transactions_as_dictionaries)
        # Proxy and Observers have different response format:
        num_sent = response.get("numOfSentTxs", 0) or response.get("txsSent", 0)
        hashes = response.get("txsHashes")
        return num_sent, hashes

    def query_contract(self, query: IContractQuery) -> ContractQueryResponse:
        request = ContractQueryRequest(query).to_http_request()
        response = self.do_post_generic('vm-values/query', request)
        return ContractQueryResponse.from_http_response(response.get('data', ''))

    def get_definition_of_fungible_token(self, token_identifier: str) -> DefinitionOfFungibleTokenOnNetwork:
        response = self.__get_token_properties(token_identifier)
        definition = DefinitionOfFungibleTokenOnNetwork.from_response_of_get_token_properties(token_identifier, response, self.address_hrp)
        return definition

    def __get_token_properties(self, identifier: str) -> List[bytes]:
        encoded_identifier = identifier.encode()
        query = ContractQuery(ESDT_CONTRACT_ADDRESS, 'getTokenProperties', 0, [encoded_identifier])
        query_response = self.query_contract(query)
        properties = query_response.get_return_data_parts()
        return properties

    def get_definition_of_token_collection(self, collection: str) -> DefinitionOfTokenCollectionOnNetwork:
        properties = self.__get_token_properties(collection)
        definition = DefinitionOfTokenCollectionOnNetwork.from_response_of_get_token_properties(collection, properties, self.address_hrp)
        return definition

    def simulate_transaction(self, transaction: ITransaction) -> SimulateResponse:
        url = "transaction/simulate"
        transactions_converter = TransactionsConverter()
        response = self.do_post_generic(url, transactions_converter.transaction_to_dictionary(transaction))
        return SimulateResponse(response)

    def get_hyperblock(self, key: Union[int, str]) -> Dict[str, Any]:
        url = f"hyperblock/by-hash/{key}"
        if str(key).isnumeric():
            url = f"hyperblock/by-nonce/{key}"

        response = self.do_get_generic(url)
        response = response.get("hyperblock", {})
        return response

    def do_get_generic(self, resource_url: str) -> GenericResponse:
        url = f'{self.url}/{resource_url}'
        response = self.do_get(url)
        return response

    def do_post_generic(self, resource_url: str, payload: Any) -> GenericResponse:
        url = f'{self.url}/{resource_url}'
        response = self.do_post(url, payload)
        return response

    def do_get(self, url: str) -> GenericResponse:
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return self.get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def do_post(self, url: str, payload: Any) -> GenericResponse:
        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return self.get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def get_data(self, parsed: Dict[str, Any], url: str) -> GenericResponse:
        err = parsed.get("error")
        code = parsed.get("code")

        if err:
            raise GenericError(url, f"code:{code}, error: {err}")

        data: Dict[str, Any] = parsed.get("data", dict())
        return GenericResponse(data)

    def _extract_error_from_response(self, response: Any):
        try:
            return response.json()
        except Exception:
            return response.text


class ContractQuery(IContractQuery):
    def __init__(self, address: IAddress, function: str, value: int, arguments: List[bytes], caller: Optional[IAddress] = None):
        self.contract = address
        self.function = function
        self.caller = caller
        self.value = value
        self.encoded_arguments = [item.hex() for item in arguments]

    def get_contract(self) -> IAddress:
        return self.contract

    def get_function(self) -> str:
        return self.function

    def get_encoded_arguments(self) -> Sequence[str]:
        return self.encoded_arguments

    def get_caller(self) -> Optional[IAddress]:
        return self.caller

    def get_value(self) -> int:
        return self.value
