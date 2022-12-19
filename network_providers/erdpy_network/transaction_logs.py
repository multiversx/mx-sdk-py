from typing import Any, Callable, Dict, List, Optional, Union

from erdpy_core import Address

from erdpy_network.interface import IAddress
from erdpy_network.resources import EmptyAddress
from erdpy_network.transaction_events import TransactionEvent


class TransactionLogs:
    def __init__(self):
        self.address: IAddress = EmptyAddress()
        self.events: List[TransactionEvent] = []

    @staticmethod
    def from_http_response(logs: Dict[str, Any]) -> 'TransactionLogs':
        result = TransactionLogs()

        address = logs.get('address', '')
        result.address = Address.from_bech32(address) if address else EmptyAddress()

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
