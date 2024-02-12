from typing import List


class TransactionEvent:
    def __init__(self,
                 address: str = "",
                 identifier: str = "",
                 topics: List[str] = [],
                 data: str = "") -> None:
        self.address = address
        self.identifier = identifier
        self.topics = topics
        self.data = data


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
                 data: str = "",
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
        self.transaction_logs = transaction_logs
