from typing import Callable, List


class TransactionEvent:
    def __init__(self,
                 address: str = "",
                 identifier: str = "",
                 topics: List[bytes] = [],
                 data_items: List[bytes] = []) -> None:
        self.address = address
        self.identifier = identifier
        self.topics = topics
        self.data_items = data_items


class TransactionLogs:
    def __init__(self,
                 address: str = "",
                 events: List[TransactionEvent] = []) -> None:
        self.address = address
        self.events = events


class SmartContractResult:
    def __init__(self,
                 sender: str = "",
                 receiver: str = "",
                 data: bytes = b"",
                 logs: TransactionLogs = TransactionLogs()) -> None:
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.logs = logs


class TransactionOutcome:
    def __init__(self,
                 transaction_results: List[SmartContractResult],
                 transaction_logs: TransactionLogs) -> None:
        self.transaction_results = transaction_results
        self.logs = transaction_logs


class SmartContractCallOutcome:
    def __init__(self,
                 function: str = "",
                 return_data_parts: List[bytes] = [],
                 return_message: str = "",
                 return_code: str = "") -> None:
        self.function = function
        self.return_data_parts = return_data_parts
        self.return_message = return_message
        self.return_code = return_code


def find_events_by_identifier(transaction_outcome: TransactionOutcome, identifier: str) -> List[TransactionEvent]:
    return find_events_by_predicate(transaction_outcome, lambda event: event.identifier == identifier)


def find_events_by_predicate(
    transaction_outcome: TransactionOutcome,
    predicate: Callable[[TransactionEvent], bool]
) -> List[TransactionEvent]:
    events = gather_all_events(transaction_outcome)
    return list(filter(predicate, events))


def gather_all_events(transaction_outcome: TransactionOutcome) -> List[TransactionEvent]:
    all_events = [*transaction_outcome.logs.events]

    for result in transaction_outcome.transaction_results:
        all_events.extend(result.logs.events)

    return all_events
