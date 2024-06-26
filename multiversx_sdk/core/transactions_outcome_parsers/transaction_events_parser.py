from types import SimpleNamespace
from typing import List, Protocol

from multiversx_sdk.core.transactions_outcome_parsers.resources import \
    TransactionEvent


class IAbi(Protocol):
    def decode_event(self, event_name: str, topics: List[bytes], data_items: List[bytes]) -> SimpleNamespace:
        ...


class TransactionEventsParser:
    def __init__(self, abi: IAbi, first_topic_as_identifier: bool = True) -> None:
        self.abi = abi

        # By default, we consider that the first topic is the event identifier.
        # This is true for log entries emitted by smart contracts:
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L270
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L283
        self.first_topic_as_identifier = first_topic_as_identifier

    def parse_events(self, events: List[TransactionEvent]) -> List[SimpleNamespace]:
        return [self.parse_event(event) for event in events]

    def parse_event(self, event: TransactionEvent) -> SimpleNamespace:
        first_topic = event.topics[0].decode() if len(event.topics) else ""
        abi_identifier = first_topic if first_topic and self.first_topic_as_identifier else event.identifier

        topics = event.topics

        if self.first_topic_as_identifier:
            topics = topics[1:]

        return self.abi.decode_event(
            event_name=abi_identifier,
            topics=topics,
            data_items=event.data_items,
        )
