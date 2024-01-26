from typing import Any, Callable, Dict, List, Optional, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress
from multiversx_sdk.network_providers.transaction_events import \
    TransactionEvent


class TransactionLogs:
    def __init__(self):
        self.address: IAddress = EmptyAddress()
        self.events: List[TransactionEvent] = []

    @staticmethod
    def from_http_response(logs: Dict[str, Any]) -> 'TransactionLogs':
        result = TransactionLogs()

        address = logs.get('address', '')
        result.address = Address.new_from_bech32(address) if address else EmptyAddress()

        events = logs.get('events', [])
        result.events = [TransactionEvent.from_http_response(item) for item in events]

        return result

    def find_first_or_none_event(self, identifier: str, predicate: Optional[Callable[[TransactionEvent], bool]] = None) -> Union[TransactionEvent, None]:
        try:
            return self.find_events(identifier, predicate)[0]
        except:
            return None

    def find_events(self, identifier: str, predicate: Optional[Callable[[TransactionEvent], bool]] = None) -> List[TransactionEvent]:
        events = [item for item in self.events if item.identifier == identifier]

        if predicate is not None:
            events = list(filter(predicate, events))

        return events

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "address": self.address.to_bech32(),
            "events": [item.to_dictionary() for item in self.events]
        }
