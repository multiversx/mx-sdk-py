import base64
from typing import Any, Dict, List, Optional

from multiversx_sdk_core import Address

from multiversx_sdk_network_providers.interface import IAddress
from multiversx_sdk_network_providers.resources import EmptyAddress


class TransactionEvent:
    def __init__(self) -> None:
        self.address: IAddress = EmptyAddress()
        self.identifier: str = ''
        self.topics: List[TransactionEventTopic] = []
        self.data_payload: Optional[TransactionEventData] = None
        self.data: str = ''

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionEvent':
        result = TransactionEvent()

        address = response.get('address', '')
        result.address = Address.from_bech32(address) if address else EmptyAddress()

        result.identifier = response.get('identifier', '')
        topics = response.get('topics', [])
        result.topics = [TransactionEventTopic(item) for item in topics]

        raw_data = base64.b64decode(response.get('responseData', b''))
        result.data_payload = TransactionEventData(raw_data)
        result.data = raw_data.decode()

        return result

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "address": self.address.bech32(),
            "identifier": self.identifier,
            "topics": [item.hex() for item in self.topics],
            "data_payload": self.data_payload.hex() if self.data_payload else "",
            "data": self.data
        }


class TransactionEventData:
    def __init__(self, raw: bytes) -> None:
        self.raw = raw

    def __str__(self) -> str:
        return self.raw.decode()

    def hex(self) -> str:
        return self.raw.hex()


class TransactionEventTopic:
    def __init__(self, topic: str) -> None:
        self.raw = base64.b64decode(topic.encode())

    def __str__(self) -> str:
        return self.raw.decode()

    def hex(self) -> str:
        return self.raw.hex()
