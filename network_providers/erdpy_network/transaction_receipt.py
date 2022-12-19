from typing import Any, Dict

from erdpy_core import Address

from erdpy_network.interface import IAddress
from erdpy_network.resources import EmptyAddress


class TransactionReceipt:
    def __init__(self):
        self.value: int = 0
        self.sender: IAddress = EmptyAddress()
        self.data: str = ''
        self.hash: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionReceipt':
        result = TransactionReceipt()

        result.value = response.get('value', 0)
        sender = response.get('sender', '')
        result.sender = Address.from_bech32(sender) if sender else EmptyAddress()

        result.data = response.get('data', '')
        result.hash = response.get('txHash', '')

        return result
