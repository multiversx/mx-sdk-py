from typing import List, Sequence

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction_parsers.interfaces import (
    IContractResultItem, IContractResults, ITransactionEvent,
    ITransactionEventTopic, ITransactionLogs, ITransactionOnNetwork)


class TransactionOnNetworkWrapper:
    def __init__(self, contract_results: IContractResults, logs: ITransactionLogs):
        self.contract_results: ContractResultsWrapper = ContractResultsWrapper(contract_results.items)
        self.logs: TransactionLogsWrapper = TransactionLogsWrapper(logs.events)

    @classmethod
    def from_transaction(cls, transaction_on_network: ITransactionOnNetwork) -> 'TransactionOnNetworkWrapper':
        return cls(transaction_on_network.contract_results, transaction_on_network.logs)

    def ensure_no_error(self):
        all_events = self.gather_all_events()

        for event in all_events:
            if event.identifier == "signalError":
                data = event.data[1:]
                message = str(event.topics[1])

                raise Exception(f"encountered signalError: {message} ({data})")

    def find_single_event_by_identifier(self, identifier: str) -> 'TransactionEventWrapper':
        all_events = self.gather_all_events()
        filtered_events = [event for event in all_events if event.identifier == identifier]

        if len(filtered_events) == 0:
            raise Exception(f"cannot find event of type: '{identifier}'")
        if len(filtered_events) > 1:
            raise Exception(f"more than one event of type '{identifier}'")

        return filtered_events[0]

    def gather_all_events(self) -> List['TransactionEventWrapper']:
        all_events: List[TransactionEventWrapper] = []
        all_events.extend(self.logs.events)

        for item in self.contract_results.items:
            all_events.extend(item.logs.events)

        return all_events


class ContractResultsWrapper:
    def __init__(self, items: Sequence[IContractResultItem]):
        self.items: List[ContractResultItemWrapper] = [ContractResultItemWrapper(item.logs) for item in items]


class ContractResultItemWrapper:
    def __init__(self, logs: 'ITransactionLogs'):
        self.logs: TransactionLogsWrapper = TransactionLogsWrapper(logs.events)


class TransactionLogsWrapper:
    def __init__(self, events: Sequence[ITransactionEvent]):
        self.events: List[TransactionEventWrapper] = [TransactionEventWrapper(event.address, event.identifier, event.topics, event.data) for event in events]


class TransactionEventWrapper:
    def __init__(self, address: IAddress, identifier: str, topics: Sequence[ITransactionEventTopic], data: str):
        self.address: IAddress = address
        self.identifier: str = identifier
        self.topics: List[TransactionEventTopicWrapper] = [TransactionEventTopicWrapper(topic.raw) for topic in topics]
        self.data: str = data


class TransactionEventTopicWrapper:
    def __init__(self, raw: bytes):
        self.raw = raw

    def __str__(self) -> str:
        return self.raw.decode("utf-8")
