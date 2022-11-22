from typing import Dict, Any
from erdpy_network.interface import IAddress
from erdpy_network.primitives import Address


class TransactionReceipt:
    def __init__(self):
        self.value: str = ''
        self.sender: IAddress = Address('')
        self.data: str = ''
        self.hash: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionReceipt':
        result = TransactionReceipt()

        result.value = response.get('value', '')
        result.sender = Address(response.get('sender', ''))
        result.data = response.get('data', '')
        result.hash = response.get('txHash', '')

        return result
