from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import requests
from requests.auth import AuthBase

from erdpy_network.accounts import AccountOnNetwork
from erdpy_network.constants import (DEFAULT_ADDRESS_HRP,
                                     ESDT_CONTRACT_ADDRESS, METACHAIN_ID)
from erdpy_network.contract_query_requests import ContractQueryRequest
from erdpy_network.contract_query_response import ContractQueryResponse
from erdpy_network.errors import GenericError
from erdpy_network.interface import IAddress, IContractQuery, ITransaction
from erdpy_network.network_config import NetworkConfig
from erdpy_network.network_status import NetworkStatus
from erdpy_network.resources import GenericResponse
from erdpy_network.token_definitions import (
    DefinitionOfFungibleTokenOnNetwork, DefinitionOfTokenCollectionOnNetwork)
from erdpy_network.tokens import (FungibleTokenOfAccountOnNetwork,
                                  NonFungibleTokenOfAccountOnNetwork)
from erdpy_network.transaction_status import TransactionStatus
from erdpy_network.transactions import TransactionOnNetwork


class ProxyNetworkProvider:
    def __init__(self, url: str, auth: Union[AuthBase, None] = None, address_hrp: str = DEFAULT_ADDRESS_HRP):
        self.url = url
        self.auth = auth
        self.address_hrp = address_hrp

    def get_network_config(self) -> NetworkConfig:
        response = self.do_get_generic('network/config')
        network_config = NetworkConfig.from_http_response(response.get('config', ''))

        return network_config

    def get_network_status(self) -> NetworkStatus:
        response = self.do_get_generic(f'network/status/{METACHAIN_ID}')
        network_status = NetworkStatus.from_http_response(response.get('status', ''))

        return network_status

    def get_account(self, address: IAddress) -> AccountOnNetwork:
        response = self.do_get_generic(f'address/{address.bech32()}')
        account = AccountOnNetwork.from_http_response(response.get('account', ''))

        return account

    def get_fungible_tokens_of_account(self, address: IAddress) -> List[FungibleTokenOfAccountOnNetwork]:
        url = f'address/{address.bech32()}/esdt'
        response = self.do_get_generic(url)
        items = response.get('esdts')
        esdts = [items[key] for key in items.keys() if items[key].get('nonce', '') == '']
        tokens = map(FungibleTokenOfAccountOnNetwork.from_http_response, esdts)

        return list(tokens)

    def get_nonfungible_tokens_of_account(self, address: IAddress) -> List[NonFungibleTokenOfAccountOnNetwork]:
        url = f'address/{address.bech32()}/esdt'
        response = self.do_get_generic(url)
        items = response.get('esdts')
        nfts = [items[key] for key in items.keys() if items[key].get('nonce', -1) > 0]
        result = map(NonFungibleTokenOfAccountOnNetwork.from_proxy_http_response, nfts)

        return list(result)

    def get_fungible_token_of_account(self, address: IAddress, identifier: str) -> FungibleTokenOfAccountOnNetwork:
        response = self.do_get_generic(f'address/{address.bech32()}/esdt/{identifier}')
        token = FungibleTokenOfAccountOnNetwork.from_http_response(response.get('tokenData'))

        return token

    def get_nonfungible_token_of_account(self, address: IAddress, collection: str, nonce: int) -> NonFungibleTokenOfAccountOnNetwork:
        response = self.do_get_generic(f'address/{address.bech32()}/nft/{collection}/nonce/{nonce}')
        token = NonFungibleTokenOfAccountOnNetwork.from_proxy_http_response_by_nonce(response.get('tokenData', ''))

        return token

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        url = f"transaction/{tx_hash}?withResults=true"
        response = self.do_get_generic(url).get('transaction', '')
        transaction = TransactionOnNetwork.from_proxy_http_response(tx_hash, response)

        return transaction

    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        response = self.do_get_generic(f'transaction/{tx_hash}/status')
        status = TransactionStatus(response.get('status', ''))

        return status

    def send_transaction(self, transaction: ITransaction) -> str:
        response = self.do_post_generic('transaction/send', transaction.to_dictionary())
        return response.get('txHash', '')

    def send_transactions(self, transactions: List[ITransaction]) -> Tuple[int, str]:
        transactions_as_dictionaries = [transaction.to_dictionary() for transaction in transactions]
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
