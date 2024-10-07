from typing import Any, Callable


class TransactionEvent:
    def __init__(self,
                 raw: dict[str, Any] = {},
                 address: str = "",
                 identifier: str = "",
                 topics: list[bytes] = [],
                 data: bytes = b"",
                 additional_data: list[bytes] = []) -> None:
        self.raw = raw
        self.address = address
        self.identifier = identifier
        self.topics = topics
        self.data = data
        self.additional_data = additional_data


class TransactionLogs:
    def __init__(self,
                 address: str = "",
                 events: list[TransactionEvent] = []) -> None:
        self.address = address
        self.events = events


class SmartContractResult:
    def __init__(self,
                 raw: dict[str, Any] = {},
                 sender: str = "",
                 receiver: str = "",
                 data: bytes = b"",
                 logs: TransactionLogs = TransactionLogs()) -> None:
        self.raw = raw
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.logs = logs


class SmartContractCallOutcome:
    def __init__(self,
                 function: str = "",
                 return_data_parts: list[bytes] = [],
                 return_message: str = "",
                 return_code: str = "") -> None:
        self.function = function
        self.return_data_parts = return_data_parts
        self.return_message = return_message
        self.return_code = return_code


class TransactionOutcome:
    def __init__(self,
                 direct_smart_contract_call_outcome: SmartContractCallOutcome = SmartContractCallOutcome(),
                 transaction_results: list[SmartContractResult] = [],
                 transaction_logs: TransactionLogs = TransactionLogs()) -> None:
        self.direct_smart_contract_call = direct_smart_contract_call_outcome
        self.transaction_results = transaction_results
        self.logs = transaction_logs


def find_events_by_identifier(transaction_outcome: TransactionOutcome, identifier: str) -> list[TransactionEvent]:
    return _find_events_by_predicate(transaction_outcome, lambda event: event.identifier == identifier)


def find_events_by_first_topic(transaction_outcome: TransactionOutcome, topic: str) -> list[TransactionEvent]:
    def is_topic_matching(event: TransactionEvent):
        if not len(event.topics):
            return False

        try:
            decoded_topic = event.topics[0].decode()
            return decoded_topic == topic
        except UnicodeDecodeError:
            return False

    return _find_events_by_predicate(transaction_outcome, is_topic_matching)


def _find_events_by_predicate(
    transaction_outcome: TransactionOutcome,
    predicate: Callable[[TransactionEvent], bool]
) -> list[TransactionEvent]:
    events = _gather_all_events(transaction_outcome)
    return list(filter(predicate, events))


def _gather_all_events(transaction_outcome: TransactionOutcome) -> list[TransactionEvent]:
    all_events = [*transaction_outcome.logs.events]

    for result in transaction_outcome.transaction_results:
        all_events.extend(result.logs.events)

    return all_events
