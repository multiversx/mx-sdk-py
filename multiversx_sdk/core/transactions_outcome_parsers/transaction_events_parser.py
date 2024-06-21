from typing import Any, List, Protocol

from multiversx_sdk.abi.abi_definition import EventDefinition
from multiversx_sdk.core.transactions_outcome_parsers.resources import \
    TransactionEvent


class IAbi(Protocol):
    def get_event(self, name: str) -> EventDefinition:
        ...

    def decode_event(self, event_definition: EventDefinition, topics: List[bytes], data_items: List[bytes]) -> List[Any]:
        ...


class TransactionEventsParser:
    def __init__(self, abi: IAbi, first_topic_as_identifier: bool = True) -> None:
        self.abi = abi

        # By default, we consider that the first topic is the event identifier.
        # This is true for log entries emitted by smart contracts:
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L270
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L283
        self.first_topic_as_identifier = first_topic_as_identifier

    def parse_events(self, events: List[TransactionEvent]) -> List[Any]:
        return [self.parse_event(event) for event in events]

    def parse_event(self, event: TransactionEvent) -> Any:
        first_topic = event.topics[0].decode() if len(event.topics) else ""
        abi_identifier = first_topic if self.first_topic_as_identifier else event.identifier

        if self.first_topic_as_identifier:
            event.topics = event.topics[1:]

        event_definition = self.abi.get_event(abi_identifier)
        return self.abi.decode_event(
            event_definition=event_definition,
            topics=event.topics,
            data_items=event.data_items,
        )
