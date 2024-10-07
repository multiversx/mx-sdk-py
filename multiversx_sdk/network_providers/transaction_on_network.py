import base64
from typing import Any, Optional

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_outcome import (SmartContractResult,
                                                     TransactionLogs)
from multiversx_sdk.network_providers.http_resources import (
    smart_contract_result_from_api_request,
    smart_contract_result_from_proxy_request, transaction_logs_from_request)
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress
from multiversx_sdk.network_providers.transaction_receipt import \
    TransactionReceipt
from multiversx_sdk.network_providers.transaction_status import \
    TransactionStatus


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

        self.receipt: TransactionReceipt = TransactionReceipt()
        self.contract_results: list[SmartContractResult] = []
        self.logs: TransactionLogs = TransactionLogs()
        self.raw_response: dict[str, Any] = {}

    def get_status(self) -> TransactionStatus:
        return self.status

    @staticmethod
    def from_api_http_response(
        tx_hash: str, response: dict[str, Any]
    ) -> "TransactionOnNetwork":
        result = TransactionOnNetwork.from_http_response(tx_hash, response)

        sc_results = response.get("results", [])
        result.contract_results = [smart_contract_result_from_api_request(result) for result in sc_results]
        result.is_completed = not result.get_status().is_pending()

        return result

    @staticmethod
    def from_proxy_http_response(
        tx_hash: str, response: dict[str, Any], process_status: Optional[TransactionStatus] = None
    ) -> "TransactionOnNetwork":
        result = TransactionOnNetwork.from_http_response(tx_hash, response)

        sc_results = response.get("results", [])
        result.contract_results = [smart_contract_result_from_proxy_request(result) for result in sc_results]

        if process_status:
            result.status = process_status
            result.is_completed = True if result.status.is_successful() or result.status.is_failed() else False

        return result

    @staticmethod
    def from_http_response(
        tx_hash: str, response: dict[str, Any]
    ) -> "TransactionOnNetwork":
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

        result.receipt = TransactionReceipt.from_http_response(
            response.get("receipt", {})
        )
        result.logs = transaction_logs_from_request(response.get("logs", {}))
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
            "smartContractResults": [item.__dict__ for item in self.contract_results],
            "logs": self.logs.__dict__,
        }
