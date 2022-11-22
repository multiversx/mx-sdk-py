from interface import IAddress
from primitives import Address
from typing import Any, List, Dict


class FungibleTokenOfAccountOnNetwork:
    def __init__(self):
        self.identifier: str = ''
        self.balance: int = 0
        self.raw_response: Any = {}

    @staticmethod
    def from_http_response(payload: Any) -> 'FungibleTokenOfAccountOnNetwork':
        result = FungibleTokenOfAccountOnNetwork()

        result.identifier = payload.get('tokenIdentifier', 0) or payload.get('identifier', 0)
        result.balance = payload.get('balance', 0)
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
        self.creator: IAddress = Address('')
        self.supply: int = 0
        self.decimals: int = 0
        self.royalties: int = 0
        self.assets: List[str] = []
        self.balance: int = 0

    @staticmethod
    def from_api_http_response(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork.from_http_response(payload)

        result.identifier = payload.get('identifier', '')
        result.collection = payload.get('collection', '')

        return result

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'NonFungibleTokenOfAccountOnNetwork':
        result = NonFungibleTokenOfAccountOnNetwork()

        result.timestamp = payload.get('timestamp', 0)
        result.attributes = payload.get('attributes', '')
        result.nonce = payload.get('nonce', 0)
        result.type = payload.get('type', '')
        result.name = payload.get('name', '')
        result.creator = Address(payload.get('creator', ''))
        result.decimals = payload.get('decimal', 0)
        result.supply = payload.get('supply', 1)
        result.royalties = payload.get('royalties', 0)
        result.assets = payload.get('assets', [])
        result.balance = payload.get('balance', 0)

        return result
