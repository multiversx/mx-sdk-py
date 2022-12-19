import base64
from typing import Any, Dict, List

from erdpy_core import Address

from erdpy_network.interface import IAddress
from erdpy_network.resources import EmptyAddress


class TransactionEvent:
    def __init__(self):
        self.address: IAddress = EmptyAddress()
        self.identifier: str = ''
        self.topics: List[TransactionEventTopic] = []
        self.data: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionEvent':
        result = TransactionEvent()

        address = response.get('address', '')
        result.address = Address.from_bech32(address) if address else EmptyAddress()

        result.identifier = response.get('identifier', '')
        topics = response.get('topics', [])
        result.topics = [TransactionEventTopic(item) for item in topics]
        result.data = base64.b64decode(response.get('responseData', '')).decode()

        return result


class TransactionEventTopic:
    def __init__(self, topic: str):
        self.raw = base64.b64decode(topic.encode())

    def __str__(self):
        return self.raw.decode()

    def hex(self):
        return self.raw.hex()
