from typing import Any, Callable, Optional, Protocol

from multiversx_sdk.core.transaction_status import TransactionStatus


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


# This class is duplicated to get rid of the circular dependency; will be removed very soon as it will not be needed anymore
class EmptyAddress:
    def to_bech32(self) -> str:
        return ""

    def to_hex(self) -> str:
        return ""


class TransactionOnNetwork:
    def __init__(self) -> None:
        self.is_completed: Optional[bool] = None
        self.hash: str = ""
        self.type: str = ""
        self.nonce: int = 0
        self.round: int = 0
        self.epoch: int = 0
        self.value: int = 0
        self.receiver: IAddress = EmptyAddress()
        self.sender: IAddress = EmptyAddress()
        self.gas_limit: int = 0
        self.gas_price: int = 0
        self.data: str = ""
        self.signature: str = ""
        self.status: TransactionStatus = TransactionStatus()
        self.timestamp: int = 0
        self.function: str = ""

        self.block_nonce: int = 0
        self.hyperblock_nonce: int = 0
        self.hyperblock_hash: str = ""

        self.contract_results: list[SmartContractResult] = []
        self.logs: TransactionLogs = TransactionLogs()
        self.raw_response: dict[str, Any] = {}

    def get_status(self) -> TransactionStatus:
        return self.status

    def to_dictionary(self) -> dict[str, Any]:
        return {
            "isCompleted": self.is_completed,
            "hash": self.hash,
            "type": self.type,
            "nonce": self.nonce,
            "round": self.round,
            "epoch": self.epoch,
            "value": self.value,
            "receiver": self.receiver.to_bech32(),
            "sender": self.sender.to_bech32(),
            "gasLimit": self.gas_limit,
            "gasPrice": self.gas_price,
            "data": self.data,
            "signature": self.signature,
            "status": self.status.status,
            "timestamp": self.timestamp,
            "blockNonce": self.block_nonce,
            "hyperblockNonce": self.hyperblock_nonce,
            "hyperblockHash": self.hyperblock_hash,
            "smartContractResults": [item.__dict__ for item in self.contract_results],
            "logs": self.logs.__dict__,
        }


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
        transaction: TransactionOnNetwork,
        predicate: Callable[[TransactionEvent], bool]
) -> list[TransactionEvent]:
    events = gather_all_events(transaction)
    return list(filter(predicate, events))


def gather_all_events(transaction: TransactionOnNetwork) -> list[TransactionEvent]:
    all_events = [*transaction.logs.events]

    for result in transaction.contract_results:
        all_events.extend(result.logs.events)

    return all_events
