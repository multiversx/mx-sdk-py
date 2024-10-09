import base64
from typing import Any, Callable, Optional, Protocol, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_status import TransactionStatus
from multiversx_sdk.network_providers.resources import EmptyAddress


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


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

        self.contract_results: ContractResults = ContractResults([])
        self.logs: TransactionLogs = TransactionLogs()
        self.raw_response: dict[str, Any] = {}

    def get_status(self) -> TransactionStatus:
        return self.status

    @staticmethod
    def from_api_http_response(
        tx_hash: str, response: dict[str, Any]
    ) -> "TransactionOnNetwork":
        result = TransactionOnNetwork.from_http_response(tx_hash, response)

        result.contract_results = ContractResults.from_api_http_response(
            response.get("results", [])
        )
        result.is_completed = not result.get_status().is_pending()

        return result

    @staticmethod
    def from_proxy_http_response(
        tx_hash: str, response: dict[str, Any], process_status: Optional[TransactionStatus] = None
    ) -> "TransactionOnNetwork":
        result = TransactionOnNetwork.from_http_response(tx_hash, response)
        result.contract_results = ContractResults.from_proxy_http_response(
            response.get("smartContractResults", [])
        )

        if process_status:
            result.status = process_status
            result.is_completed = True if result.status.is_successful() or result.status.is_failed() else False

        return result

    @staticmethod
    def from_http_response(tx_hash: str, response: dict[str, Any]) -> "TransactionOnNetwork":
        result = TransactionOnNetwork()

        result.hash = tx_hash
        result.type = response.get("type", "")
        result.nonce = response.get("nonce", 0)
        result.round = response.get("round", 0)
        result.epoch = response.get("epoch", 0)
        result.value = response.get("value", 0)

        sender = response.get("sender", "")
        result.sender = Address.new_from_bech32(sender) if sender else EmptyAddress()

        receiver = response.get("receiver", "")
        result.receiver = Address.new_from_bech32(receiver) if receiver else EmptyAddress()

        result.gas_price = response.get("gasPrice", 0)
        result.gas_limit = response.get("gasLimit", 0)

        data = response.get("data", "") or ""
        result.function = response.get("function", "")

        result.data = base64.b64decode(data).decode()
        result.status = TransactionStatus(response.get("status"))
        result.timestamp = response.get("timestamp", 0)

        result.block_nonce = response.get("blockNonce", 0)
        result.hyperblock_nonce = response.get("hyperblockNonce", 0)
        result.hyperblock_hash = response.get("hyperblockHash", "")

        result.logs = TransactionLogs.from_http_response(response.get("logs", {}))
        result.raw_response = response

        return result

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
            "smartContractResults": [item.to_dictionary() for item in self.contract_results.items],
            "logs": self.logs.to_dictionary(),
        }


class TransactionEvent:
    def __init__(self) -> None:
        self.address: IAddress = EmptyAddress()
        self.identifier: str = ''
        self.topics: list[TransactionEventTopic] = []
        self.data_payload: Optional[TransactionEventData] = None
        self.data: str = ''
        self.additional_data: list[TransactionEventData] = []

    @staticmethod
    def from_http_response(response: dict[str, Any]) -> 'TransactionEvent':
        result = TransactionEvent()

        address = response.get('address', '')
        result.address = Address.new_from_bech32(address) if address else EmptyAddress()

        result.identifier = response.get('identifier', '')
        topics = response.get('topics', [])
        result.topics = [TransactionEventTopic(item) for item in topics]

        raw_data = base64.b64decode(response.get('responseData', b''))
        result.data_payload = TransactionEventData(raw_data)
        result.data = raw_data.decode()

        additional_data: Any = response.get("additionalData", [])
        if additional_data is None:
            additional_data = []
        result.additional_data = [TransactionEventData(base64.b64decode(data)) for data in additional_data]

        return result

    def to_dictionary(self) -> dict[str, Any]:
        return {
            "address": self.address.to_bech32(),
            "identifier": self.identifier,
            "topics": [item.hex() for item in self.topics],
            "data_payload": self.data_payload.hex() if self.data_payload else "",
            "data": self.data,
            "additional_data": [data.hex() for data in self.additional_data]
        }


class TransactionEventData:
    def __init__(self, raw: bytes) -> None:
        self.raw = raw

    def __str__(self) -> str:
        return self.raw.decode()

    def hex(self) -> str:
        return self.raw.hex()


class TransactionEventTopic:
    def __init__(self, topic: str) -> None:
        self.raw = base64.b64decode(topic.encode())

    def __str__(self) -> str:
        return self.raw.decode()

    def hex(self) -> str:
        return self.raw.hex()


class TransactionLogs:
    def __init__(self):
        self.address: IAddress = EmptyAddress()
        self.events: list[TransactionEvent] = []

    @staticmethod
    def from_http_response(logs: dict[str, Any]) -> 'TransactionLogs':
        result = TransactionLogs()

        address = logs.get('address', '')
        result.address = Address.new_from_bech32(address) if address else EmptyAddress()

        events = logs.get('events', [])
        result.events = [TransactionEvent.from_http_response(item) for item in events]

        return result

    def find_first_or_none_event(self, identifier: str, predicate: Optional[Callable[[TransactionEvent], bool]] = None) -> Union[TransactionEvent, None]:
        try:
            return self.find_events(identifier, predicate)[0]
        except:
            return None

    def find_events(self, identifier: str, predicate: Optional[Callable[[TransactionEvent], bool]] = None) -> list[TransactionEvent]:
        events = [item for item in self.events if item.identifier == identifier]

        if predicate is not None:
            events = list(filter(predicate, events))

        return events

    def to_dictionary(self) -> dict[str, Any]:
        return {
            "address": self.address.to_bech32(),
            "events": [item.to_dictionary() for item in self.events]
        }


class ContractResults:
    def __init__(self, items: list["ContractResultItem"]):
        self.items = items
        self.items.sort(key=lambda x: x.nonce, reverse=False)

    @staticmethod
    def from_api_http_response(results: list[Any]) -> "ContractResults":
        items = [ContractResultItem.from_api_http_response(item) for item in results]
        return ContractResults(items)

    @staticmethod
    def from_proxy_http_response(results: list[Any]) -> "ContractResults":
        items = list(map(ContractResultItem.from_proxy_http_response, results))
        return ContractResults(items)


class ContractResultItem:
    def __init__(self):
        self.hash: str = ""
        self.nonce: int = 0
        self.value: int = 0
        self.receiver: IAddress = EmptyAddress()
        self.sender: IAddress = EmptyAddress()
        self.data: str = ""
        self.previous_hash: str = ""
        self.original_hash: str = ""
        self.gas_limit: int = 0
        self.gas_price: int = 0
        self.call_type: int = 0
        self.return_message: str = ""
        self.is_refund = False
        self.logs: TransactionLogs = TransactionLogs()

    def to_dictionary(self) -> dict[str, Any]:
        return {
            "hash": self.hash,
            "nonce": self.nonce,
            "value": self.value,
            "receiver": self.receiver.to_bech32(),
            "sender": self.sender.to_bech32(),
            "data": self.data,
            "previousHash": self.previous_hash,
            "originalHash": self.original_hash,
            "gasLimit": self.gas_limit,
            "gasPrice": self.gas_price,
            "callType": self.call_type,
            "returnMessage": self.return_message,
            "isRefund": self.is_refund,
            "logs": self.logs.to_dictionary()
        }

    @staticmethod
    def from_api_http_response(response: Any) -> "ContractResultItem":
        item = ContractResultItem._from_http_response(response)

        item.data = base64.b64decode(item.data.encode()).decode()
        item.call_type = int(item.call_type)

        return item

    @staticmethod
    def from_proxy_http_response(response: Any) -> "ContractResultItem":
        item = ContractResultItem._from_http_response(response)

        return item

    @staticmethod
    def _from_http_response(response: dict[str, Any]) -> "ContractResultItem":
        item = ContractResultItem()

        item.hash = response.get("hash", "")
        item.nonce = response.get("nonce", 0)
        item.value = int(response.get("value", 0))

        sender = response.get("sender", "")
        item.sender = Address.new_from_bech32(sender) if sender else EmptyAddress()

        receiver = response.get("receiver", "")
        item.receiver = Address.new_from_bech32(receiver) if receiver else EmptyAddress()

        item.previous_hash = response.get("prevTxHash", "")
        item.original_hash = response.get("originalTxHash", "")
        item.gas_limit = response.get("gasLimit", 0)
        item.gas_price = response.get("gasPrice", 0)
        item.data = response.get("data", "")
        item.call_type = response.get("callType", 0)
        item.return_message = response.get("returnMessage", "")
        item.is_refund = response.get("isRefund", False)

        item.logs = TransactionLogs.from_http_response(response.get("logs", {}))

        return item
