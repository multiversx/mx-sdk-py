from typing import List, Any, Dict, Callable, Union, Optional
from erdpy_network.interface import IAddress
from erdpy_core import Address
from erdpy_network.transaction_events import TransactionEvent


class TransactionLogs:
    def __init__(self):
        self.address: IAddress = Address.zero()
        self.events: List[TransactionEvent] = []

    @staticmethod
    def from_http_response(logs: Dict[str, Any]) -> 'TransactionLogs':
        result = TransactionLogs()

        address = logs.get('address', '')
        result.address = Address.from_bech32(address) if address else Address.zero()

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
