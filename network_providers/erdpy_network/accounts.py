from typing import Any, Dict
from interface import IAddress
from primitives import Address


class AccountsOnNetwork:
    def __init__(self):
        self.address: IAddress = Address('')
        self.nonce: int = 0
        self.balance: int = 0
        self.code: str = ''
        self.username: str = ''

    @staticmethod
    def from_http_response(payload: Dict[str, Any]) -> 'AccountsOnNetwork':
        result = AccountsOnNetwork()

        result.address = payload.get('address', '')
        result.nonce = payload.get('nonce', 0)
        result.balance = payload.get('balance', 0)
        result.code = payload.get('code', '')
        result.username = payload.get('username', '')

        return result
