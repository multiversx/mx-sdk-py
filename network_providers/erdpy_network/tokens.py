from typing import Any, Dict, List

from erdpy_core import Address

from erdpy_network.interface import IAddress
from erdpy_network.resources import EmptyAddress
from erdpy_network.utils import decimal_to_padded_hex


class FungibleTokenOfAccountOnNetwork:
    def __init__(self):
        self.identifier: str = ''
        self.balance: int = 0
        self.raw_response: Any = {}

    @staticmethod
    def from_http_response(payload: Any) -> 'FungibleTokenOfAccountOnNetwork':
        result = FungibleTokenOfAccountOnNetwork()

        result.identifier = payload.get('tokenIdentifier', '') or payload.get('identifier', '')
        result.balance = int(payload.get('balance', 0))
        result.raw_response = payload

        return result


class NonFungibleTokenOfAccountOnNetwork:
    def __init__(self):
        self.identifier: str = ''
        self.collection: str = ''
        self.timestamp: int = 0
        self.attributes: str = ''
        self.nonce: int = 0
        self.type: str = ''
        self.name: str = ''
        self.creator: IAddress = EmptyAddress()
        self.supply: int = 0
        self.decimals: int = 0
        self.royalties: float = 0
        self.assets: List[str] = []
        self.balance: int = 0

    @staticmethod
    def from_api_http_response(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork.from_http_response(payload)

        result.identifier = payload.get('identifier', '')
        result.collection = payload.get('collection', '')

        return result

    @staticmethod
    def from_proxy_http_response(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork.from_http_response(payload)

        result.identifier = payload.get('tokenIdentifier', '')
        result.collection = NonFungibleTokenOfAccountOnNetwork.parse_collection_from_identifier(result.identifier)
        result.royalties = float(payload.get('royalties', 0)) / 100

        return result

    @staticmethod
    def from_proxy_http_response_by_nonce(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork.from_proxy_http_response(payload)

        nonce_as_hex = decimal_to_padded_hex(payload.get('nonce', 0))
        token_identifier = payload.get('tokenIdentifier', '')

        result.identifier = f'{token_identifier}-{nonce_as_hex}'
        result.collection = token_identifier
        result.royalties = float(payload.get('royalties', 0)) / 100

        return result

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork()

        result.timestamp = payload.get('timestamp', 0)
        result.attributes = payload.get('attributes', '')
        result.nonce = int(payload.get('nonce', 0))
        result.type = payload.get('type', '')
        result.name = payload.get('name', '')

        creator = payload.get('creator', '')
        result.creator = Address.from_bech32(creator) if creator else EmptyAddress()

        result.decimals = payload.get('decimals', 0)
        result.supply = payload.get('supply', 1)
        result.royalties = payload.get('royalties', 0)
        result.assets = payload.get('assets', [])
        result.balance = int(payload.get('balance', 0))

        return result

    @staticmethod
    def parse_collection_from_identifier(identifier: str) -> str:
        parts = identifier.split('-')
        collection = '-'.join(parts[0:2])

        return collection
