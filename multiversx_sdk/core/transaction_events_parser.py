from types import SimpleNamespace

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core.transaction_on_network import TransactionEvent


class TransactionEventsParser:
    def __init__(self, abi: Abi, first_topic_as_identifier: bool = True) -> None:
        self.abi = abi
        # By default, we consider that the first topic is the event identifier.
        # This is true for log entries emitted by smart contracts:
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L270
        # https://github.com/multiversx/mx-chain-vm-go/blob/v1.5.27/vmhost/contexts/output.go#L283
        self.first_topic_as_identifier = first_topic_as_identifier

    def parse_events(self, events: list[TransactionEvent]) -> list[SimpleNamespace]:
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
            additional_data=event.additional_data,
        )
