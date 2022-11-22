import requests
from requests.auth import AuthBase
from typing import Union, Dict, List, Any
from erdpy_network.errors import GenericError
from erdpy_network.pairs import PairOnNetwork
from erdpy_network.core import NetworkProvider
from erdpy_network.primitives import Nonce
from erdpy_network.network_stake import NetworkStake
from erdpy_network.accounts import AccountsOnNetwork
from erdpy_network.http_facade import _extract_error_from_response
from erdpy_network.contract_query_requests import ContractQueryRequest
from erdpy_network.contract_query_response import ContractQueryResponse
from erdpy_network.network_general_statistic import NetworkGeneralStatistics
from erdpy_network.tokens import FungibleTokenOfAccountOnNetwork, NonFungibleTokenOfAccountOnNetwork
from erdpy_network.token_definitions import DefinitionOfFungibleTokenOnNetwork, DefinitionOfTokenCollectionOnNetwork
from erdpy_network.transactions import TransactionOnNetwork
from erdpy_network.interface import IAddress, IPagination, IContractQuery, ITransaction
from erdpy_network.transaction_status import TransactionStatus


class ApiNetworkProvider(NetworkProvider):
    def __init__(self, url: str):
        super().__init__(url)

    def get_network_stake_statistics(self) -> NetworkStake:
        response = NetworkProvider.do_get_generic(self, 'stake')
        network_stake = NetworkStake.from_http_response(response.to_dictionary())

        return network_stake

    def get_network_general_statistics(self) -> NetworkGeneralStatistics:
        response = NetworkProvider.do_get_generic(self, 'stats')
        network_stats = NetworkGeneralStatistics.from_http_response(response.to_dictionary())

        return network_stats

    def get_account(self, address: IAddress) -> AccountsOnNetwork:
        response = NetworkProvider.do_get_generic(self, f'accounts/{address.bech32()}')
        account = AccountsOnNetwork.from_http_response(response.to_dictionary())

        return account

    def get_fungible_tokens_of_account(self, address: IAddress, pagination: IPagination = None):
        default_pagination = IPagination()
        pagination = pagination if pagination is not None else default_pagination

        url = f'accounts/{address.bech32()}/tokens?{self.__build_pagination_params(pagination)}'
        response = self.do_get_generic(url)
        result = map(FungibleTokenOfAccountOnNetwork.from_http_response, response)

        return list(result)

    def get_nonfungible_tokens_of_account(self, address: IAddress, pagination: IPagination = None):
        default_pagination = IPagination()
        pagination = pagination if pagination is not None else default_pagination

        url = f'accounts/{address.bech32()}/nfts?{self.__build_pagination_params(pagination)}'
        response = self.do_get_generic(url)
        result = map(NonFungibleTokenOfAccountOnNetwork.from_api_http_response, response)

        return list(result)

    def get_fungible_token_of_account(self, address: IAddress, token_identifier: str):
        url = f'accounts/{address.bech32()}/tokens/{token_identifier}'
        response = self.do_get_generic(url)
        result = FungibleTokenOfAccountOnNetwork.from_http_response(response)

        return result

    def get_nonfungible_token_of_account(self, address: IAddress, collection: str, nonce: int):
        nonce_as_hex = Nonce(nonce).hex()
        url = f'accounts/{address.bech32()}/nfts/{collection}-{nonce_as_hex}'
        response = self.do_get_generic(url)
        result = NonFungibleTokenOfAccountOnNetwork.from_api_http_response(response)

        return result

    def get_mex_pairs(self, pagination: IPagination = None):
        url = 'mex/pairs'
        if pagination:
            url = f'{url}?from={pagination.start}&size={pagination.size}'

        response = self.do_get_generic(url)
        result = map(PairOnNetwork.from_api_http_response, response)

        return list(result)

    def get_definition_of_fungible_token(self, token_identifier: str):
        response = self.do_get_generic(f'tokens/{token_identifier}')
        result = DefinitionOfFungibleTokenOnNetwork.from_api_http_response(response)

        return result

    def get_definition_of_token_collection(self, collection: str):
        response = self.do_get_generic(f'collections/{collection}')
        result = DefinitionOfTokenCollectionOnNetwork.from_api_http_response(response)

        return result

    def get_non_fungible_token(self, collection: str, nonce: int):
        nonce_as_hex = Nonce(nonce).hex()
        response = self.do_get_generic(f'nfts/{collection}-{nonce_as_hex}')
        result = NonFungibleTokenOfAccountOnNetwork.from_api_http_response(response)

        return result

    def query_contract(self, query: IContractQuery):
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

    def send_transaction(self, payload: ITransaction) -> str:
        url = f'{self.url}/transaction/send'
        response = self.do_post_generic(url, payload)
        tx_hash = response.get('txHash', '')

        return tx_hash

    def __build_pagination_params(self, pagination: IPagination):
        return f'from={pagination.start}&size={pagination.size}'

    def do_get_generic(self, resource_url: str):
        response = self.do_get(f'{self.url}/{resource_url}')
        return response

    def do_post_generic(self, resource_url: str, payload: Any):
        response = self.do_post(resource_url, payload)
        return response

    def do_get(self, url: str, auth: Union[AuthBase, None] = None):
        try:
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            parsed = response.json()
            return self._get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = _extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def do_post(self, url: str, payload: Any):
        url = f'{self.url}/{url}'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            parsed = response.json()
            return self._get_data(parsed, url)
        except requests.HTTPError as err:
            error_data = _extract_error_from_response(err.response)
            raise GenericError(url, error_data)
        except requests.ConnectionError as err:
            raise GenericError(url, err)
        except Exception as err:
            raise GenericError(url, err)

    def _get_data(self, parsed: Union[Dict, List], url: str):
        if isinstance(parsed, List):
            return parsed
        else:
            err = parsed.get("error", None)
            if err:
                code = parsed.get("statusCode")
                raise GenericError(url, f"code:{code}, error: {err}")
            else:
                return parsed
