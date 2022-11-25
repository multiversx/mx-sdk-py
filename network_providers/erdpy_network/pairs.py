from typing import Any, Dict
from erdpy_network.interface import IAddress
from erdpy_core import Address


class PairOnNetwork:
    def __init__(self):
        self.address: IAddress = Address.zero()
        self.id: str = ''
        self.symbol: str = ''
        self.name: str = ''
        self.price: float = 0
        self.base_id: str = ''
        self.base_price: float = 0
        self.base_symbol: str = ''
        self.base_name: str = ''
        self.quote_id: str = ''
        self.quote_price: float = 0
        self.quote_symbol: str = ''
        self.quote_name: str = ''
        self.total_value: float = 0
        self.volume_24h: float = 0
        self.state: str = ''
        self.type: str = ''
        self.raw_response: Any = {}

    @staticmethod
    def from_api_http_response(payload: Dict[str, Any]) -> 'PairOnNetwork':
        result = PairOnNetwork()

        address = payload.get('address', '')
        result.address = Address.from_bech32(address) if address else Address.zero()

        result.id = payload.get('id', '')
        result.symbol = payload.get('symbol', '')
        result.name = payload.get('name', '')
        result.price = payload.get('price', 0)
        result.base_id = payload.get('baseId', '')
        result.base_price = payload.get('basePrice', 0)
        result.base_symbol = payload.get('baseSymbol' '')
        result.base_name = payload.get('baseName', '')
        result.quote_id = payload.get('quoteId', '')
        result.quote_price = payload.get('quotePrice', 0)
        result.quote_symbol = payload.get('quoteSymbol', '')
        result.quote_name = payload.get('quoteName', '')
        result.total_value = payload.get('totalValue', 0)
        result.volume_24h = payload.get('volume24h', 0)
        result.state = payload.get('state', '')
        result.type = payload.get('type', '')

        result.raw_response = payload

        return result
