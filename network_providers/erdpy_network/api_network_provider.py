from typing import Any, Dict, List, Optional, Tuple, Union, cast

import requests
from requests.auth import AuthBase

from erdpy_network.accounts import AccountOnNetwork
from erdpy_network.config import DefaultPagination
from erdpy_network.constants import DEFAULT_ADDRESS_HRP
from erdpy_network.contract_query_requests import ContractQueryRequest
from erdpy_network.contract_query_response import ContractQueryResponse
from erdpy_network.errors import GenericError
from erdpy_network.interface import (IAddress, IContractQuery, IPagination,
                                     ITransaction)
from erdpy_network.network_config import NetworkConfig
from erdpy_network.network_general_statistics import NetworkGeneralStatistics
from erdpy_network.network_stake import NetworkStake
from erdpy_network.network_status import NetworkStatus
from erdpy_network.proxy_network_provider import ProxyNetworkProvider
from erdpy_network.token_definitions import (
    DefinitionOfFungibleTokenOnNetwork, DefinitionOfTokenCollectionOnNetwork)
from erdpy_network.tokens import (FungibleTokenOfAccountOnNetwork,
                                  NonFungibleTokenOfAccountOnNetwork)
from erdpy_network.transaction_status import TransactionStatus
from erdpy_network.transactions import TransactionOnNetwork
from erdpy_network.utils import decimal_to_padded_hex


class ApiNetworkProvider:
    def __init__(self, url: str, auth: Union[AuthBase, None] = None, address_hrp: str = DEFAULT_ADDRESS_HRP):
        self.url = url
        self.backing_proxy = ProxyNetworkProvider(url, auth, address_hrp)
        self.auth = auth

    def get_network_config(self) -> NetworkConfig:
        return self.backing_proxy.get_network_config()

    def get_network_status(self) -> NetworkStatus:
        return self.backing_proxy.get_network_status()

    def get_network_stake_statistics(self) -> NetworkStake:
        response = self.do_get_generic('stake')
        network_stake = NetworkStake.from_http_response(response)

        return network_stake

    def get_network_general_statistics(self) -> NetworkGeneralStatistics:
        response = self.do_get_generic('stats')
        network_stats = NetworkGeneralStatistics.from_http_response(response)

        return network_stats

    def get_account(self, address: IAddress) -> AccountOnNetwork:
        response = self.do_get_generic(f'accounts/{address.bech32()}')
        account = AccountOnNetwork.from_http_response(response)

        return account

    def get_fungible_tokens_of_account(self, address: IAddress, pagination: Optional[IPagination] = None) -> List[FungibleTokenOfAccountOnNetwork]:
        default_pagination = DefaultPagination()
        pagination = pagination if pagination is not None else default_pagination

        url = f'accounts/{address.bech32()}/tokens?{self._build_pagination_params(pagination)}'
        response = self.do_get_generic_collection(url)
        result = map(FungibleTokenOfAccountOnNetwork.from_http_response, response)

        return list(result)

    def get_nonfungible_tokens_of_account(self, address: IAddress, pagination: Optional[IPagination] = None) -> List[NonFungibleTokenOfAccountOnNetwork]:
        default_pagination = DefaultPagination()
        pagination = pagination if pagination is not None else default_pagination

        url = f'accounts/{address.bech32()}/nfts?{self._build_pagination_params(pagination)}'
        response = self.do_get_generic_collection(url)
        result = map(NonFungibleTokenOfAccountOnNetwork.from_api_http_response, response)

        return list(result)

    def get_fungible_token_of_account(self, address: IAddress, token_identifier: str) -> FungibleTokenOfAccountOnNetwork:
        url = f'accounts/{address.bech32()}/tokens/{token_identifier}'
        response = self.do_get_generic(url)
        result = FungibleTokenOfAccountOnNetwork.from_http_response(response)

        return result

    def get_nonfungible_token_of_account(self, address: IAddress, collection: str, nonce: int) -> NonFungibleTokenOfAccountOnNetwork:
        nonce_as_hex = decimal_to_padded_hex(nonce)
        url = f'accounts/{address.bech32()}/nfts/{collection}-{nonce_as_hex}'
        response = self.do_get_generic(url)
        result = NonFungibleTokenOfAccountOnNetwork.from_api_http_response(response)

        return result

    def get_definition_of_fungible_token(self, token_identifier: str) -> DefinitionOfFungibleTokenOnNetwork:
        response = self.do_get_generic(f'tokens/{token_identifier}')
        result = DefinitionOfFungibleTokenOnNetwork.from_api_http_response(response)

        return result

    def get_definition_of_token_collection(self, collection: str) -> DefinitionOfTokenCollectionOnNetwork:
        response = self.do_get_generic(f'collections/{collection}')
        result = DefinitionOfTokenCollectionOnNetwork.from_api_http_response(response)

        return result

    def get_non_fungible_token(self, collection: str, nonce: int) -> NonFungibleTokenOfAccountOnNetwork:
        nonce_as_hex = decimal_to_padded_hex(nonce)
        response = self.do_get_generic(f'nfts/{collection}-{nonce_as_hex}')
        result = NonFungibleTokenOfAccountOnNetwork.from_api_http_response(response)

        return result

    def query_contract(self, query: IContractQuery) -> ContractQueryResponse:
        request = ContractQueryRequest(query).to_http_request()
        response = self.do_post_generic('query', request)

        return ContractQueryResponse.from_http_response(response)

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        response = self.do_get_generic(f'transactions/{tx_hash}')
        transaction = TransactionOnNetwork.from_api_http_response(tx_hash, response)

        return transaction

    def get_transaction_status(self, tx_hash: str) -> TransactionStatus:
        response = self.do_get_generic(f'transactions/{tx_hash}?fields=status')
        status = TransactionStatus(response.get('status', ''))

        return status

    def send_transaction(self, transaction: ITransaction) -> str:
        url = f'{self.url}/transactions'
        response = self.do_post_generic(url, transaction.to_dictionary())
        tx_hash: str = response.get('txHash', '')

        return tx_hash

    def send_transactions(self, transactions: List[ITransaction]) -> Tuple[int, str]:
        response = self.backing_proxy.send_transactions(transactions)

        return response

    def _build_pagination_params(self, pagination: IPagination) -> str:
        return f'from={pagination.get_start()}&size={pagination.get_size()}'

    def do_get_generic(self, resource_url: str) -> Dict[str, Any]:
        url = f'{self.url}/{resource_url}'
        response = self.__do_get(url)
        return response

    def do_get_generic_collection(self, resource_url: str) -> List[Dict[str, Any]]:
        url = f'{self.url}/{resource_url}'
        response = self.__do_get(url)
        return response

    def do_post_generic(self, resource_url: str, payload: Any) -> Dict[str, Any]:
        url = f'{self.url}/{resource_url}'
        response = self.do_post(url, payload)
        return response

    def __do_get(self, url: str) -> Any:
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return self._get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def do_post(self, url: str, payload: Any) -> Dict[str, Any]:
        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            parsed = response.json()
            return cast(Dict[str, Any], self._get_data(parsed, url))
        except requests.HTTPError as err:
            error_data = self._extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def _get_data(self, parsed: Any, url: str) -> Any:
        if isinstance(parsed, List):
            return cast(Any, parsed)
        else:
            err = parsed.get("error", None)
            if err:
                code = parsed.get("statusCode")
                raise GenericError(url, f"code:{code}, error: {err}")
            else:
                return parsed

    def _extract_error_from_response(self, response: Any):
        try:
            return response.json()
        except Exception:
            return response.text
