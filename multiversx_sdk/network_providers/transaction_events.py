import base64
from typing import Any, Dict, List, Optional

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress


class TransactionEvent:
    def __init__(self) -> None:
        self.address: IAddress = EmptyAddress()
        self.identifier: str = ''
        self.topics: List[TransactionEventTopic] = []
        self.data_payload: Optional[TransactionEventData] = None
        self.data: str = ''
        self.additional_data: List[TransactionEventData] = []

    @staticmethod
    def from_http_response(response: Dict[str, Any]) -> 'TransactionEvent':
        result = TransactionEvent()

        address = response.get('address', '')
        result.address = Address.new_from_bech32(address) if address else EmptyAddress()

        result.identifier = response.get('identifier', '')
        topics = response.get('topics', [])
        result.topics = [TransactionEventTopic(item) for item in topics]

        raw_data = base64.b64decode(response.get('responseData', b''))
        result.data_payload = TransactionEventData(raw_data)
        result.data = raw_data.decode()

        additional_data: Any = response.get("additionalData", [])
        if additional_data is None:
            additional_data = []
        result.additional_data = [TransactionEventData(base64.b64decode(data)) for data in additional_data]

        return result

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "address": self.address.to_bech32(),
            "identifier": self.identifier,
            "topics": [item.hex() for item in self.topics],
            "data_payload": self.data_payload.hex() if self.data_payload else "",
            "data": self.data,
            "additional_data": [data.hex() for data in self.additional_data]
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
