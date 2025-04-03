from dataclasses import dataclass
from typing import Any, Callable

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_status import TransactionStatus


@dataclass
class TransactionEvent:
    raw: dict[str, Any]
    address: Address
    identifier: str
    topics: list[bytes]
    data: bytes
    additional_data: list[bytes]


@dataclass
class TransactionLogs:
    address: Address
    events: list[TransactionEvent]


@dataclass
class SmartContractResult:
    raw: dict[str, Any]
    sender: Address
    receiver: Address
    data: bytes
    logs: TransactionLogs


@dataclass
class TransactionOnNetwork:
    raw: dict[str, Any]
    sender: Address
    receiver: Address
    hash: bytes
    nonce: int
    round: int
    epoch: int
    timestamp: int
    block_hash: bytes
    miniblock_hash: bytes
    sender_shard: int
    receiver_shard: int
    value: int
    gas_limit: int
    gas_price: int
    function: str
    data: bytes
    version: int
    options: int
    signature: bytes
    status: TransactionStatus
    smart_contract_results: list[SmartContractResult]
    logs: TransactionLogs


def find_events_by_identifier(transaction: TransactionOnNetwork, identifier: str) -> list[TransactionEvent]:
    return find_events_by_predicate(transaction, lambda event: event.identifier == identifier)


def find_events_by_first_topic(transaction: TransactionOnNetwork, topic: str) -> list[TransactionEvent]:
    def is_topic_matching(event: TransactionEvent):
        if not len(event.topics):
            return False

        try:
            decoded_topic = event.topics[0].decode()
            return decoded_topic == topic
        except UnicodeDecodeError:
            return False

    return find_events_by_predicate(transaction, is_topic_matching)


def find_events_by_predicate(
    transaction: TransactionOnNetwork, predicate: Callable[[TransactionEvent], bool]
) -> list[TransactionEvent]:
    events = gather_all_events(transaction)
    return list(filter(predicate, events))


def gather_all_events(transaction: TransactionOnNetwork) -> list[TransactionEvent]:
    all_events = [*transaction.logs.events]

    for result in transaction.smart_contract_results:
        all_events.extend(result.logs.events)

    return all_events
