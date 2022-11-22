from typing import List, Any, Dict
from erdpy_network.interface import IAddress
from erdpy_network.primitives import Address
from erdpy_network.transaction_events import TransactionEvent


class TransactionLogs:
    def __init__(self):
        self.address: IAddress = Address('')
        self.events: List[TransactionEvent] = []

    @staticmethod
    def from_http_response(logs: Dict[str, Any]) -> 'TransactionLogs':
        result = TransactionLogs()

        result.address = Address(logs.get('address', ''))
        events = logs.get('events', [])
        result.events = [TransactionEvent.from_http_response(item) for item in events]

        return result
