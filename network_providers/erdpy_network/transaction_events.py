import base64
from typing import List, Any, Dict
from erdpy_network.interface import IAddress
from erdpy_network.primitives import Address


class TransactionEvent:
    def __init__(self):
        self.address: IAddress = Address('')
        self.identifier: str = ''
        self.topics: List[TransactionEventTopic] = []
        self.data: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionEvent':
        result = TransactionEvent()

        result.address = Address(response.get('address', ''))
        result.identifier = response.get('identifier', '')
        topics = response.get('topics', [])
        result.topics = [TransactionEventTopic(item) for item in topics]
        result.data = base64.b64decode(response.get('responseData', '').encode())

        return result


class TransactionEventTopic:
    def __init__(self, topic: str):
        self.raw = base64.b64decode(topic.encode())

    def to_string(self):
        return str(self.raw, 'utf-8')

    def hex(self):
        return hex(int(self.raw, 16))

    def value_of(self):
        return self.raw
