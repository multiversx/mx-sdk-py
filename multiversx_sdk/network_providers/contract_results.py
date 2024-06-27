import base64
from typing import Any, Dict, List

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress
from multiversx_sdk.network_providers.transaction_logs import TransactionLogs


class ContractResults:
    def __init__(self, items: List["ContractResultItem"]):
        self.items = items
        self.items.sort(key=lambda x: x.nonce, reverse=False)

    @staticmethod
    def from_api_http_response(results: List[Any]) -> "ContractResults":
        items = [ContractResultItem.from_api_http_response(item) for item in results]
        return ContractResults(items)

    @staticmethod
    def from_proxy_http_response(results: List[Any]) -> "ContractResults":
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

    def to_dictionary(self) -> Dict[str, Any]:
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
    def _from_http_response(response: Dict[str, Any]) -> "ContractResultItem":
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
