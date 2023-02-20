import base64
from typing import Any, Dict, List

from multiversx_sdk_core import Address

from multiversx_sdk_network_providers.interface import IAddress
from multiversx_sdk_network_providers.resources import EmptyAddress


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

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "address": self.address.bech32(),
            "identifier": self.identifier,
            "topics": [item.__str__() for item in self.topics],
            "data": self.data
        }


class TransactionEventTopic:
    def __init__(self, topic: str):
        self.raw = base64.b64decode(topic.encode())

    def __str__(self):
        return base64.b64encode(self.raw).decode()

    def hex(self):
        return self.raw.hex()
