from typing import Dict, Any
from erdpy_network.interface import IAddress
from erdpy_core import Address


class TransactionReceipt:
    def __init__(self):
        self.value: str = ''
        self.sender: IAddress = Address.zero()
        self.data: str = ''
        self.hash: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionReceipt':
        result = TransactionReceipt()

        result.value = response.get('value', '')
        sender = response.get('sender', '')
        result.sender = Address.from_bech32(sender) if sender else Address.zero()

        result.data = response.get('data', '')
        result.hash = response.get('txHash', '')

        return result
