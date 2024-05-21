import base64
from typing import Any, Dict, Optional, Protocol, Sequence

from multiversx_sdk.core.address import Address
from multiversx_sdk.network_providers.contract_results import ContractResults
from multiversx_sdk.network_providers.interface import IAddress
from multiversx_sdk.network_providers.resources import EmptyAddress
from multiversx_sdk.network_providers.transaction_logs import TransactionLogs
from multiversx_sdk.network_providers.transaction_receipt import \
    TransactionReceipt
from multiversx_sdk.network_providers.transaction_status import \
    TransactionStatus


class ITransaction(Protocol):
    sender: str
    receiver: str
    gas_limit: int
    chain_id: str
    nonce: int
    value: int
    sender_username: str
    receiver_username: str
    gas_price: int
    data: bytes
    version: int
    options: int
    guardian: str
    signature: bytes
    guardian_signature: bytes
    relayer: str

    @property
    def inner_transactions(self) -> Sequence["ITransaction"]:
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

        self.receipt: TransactionReceipt = TransactionReceipt()
        self.contract_results: ContractResults = ContractResults([])
        self.logs: TransactionLogs = TransactionLogs()
        self.raw_response: Dict[str, Any] = {}

    def get_status(self) -> TransactionStatus:
        return self.status

    @staticmethod
    def from_api_http_response(
        tx_hash: str, response: Dict[str, Any]
    ) -> "TransactionOnNetwork":
        result = TransactionOnNetwork.from_http_response(tx_hash, response)

        result.contract_results = ContractResults.from_api_http_response(
            response.get("results", [])
        )
        result.is_completed = not result.get_status().is_pending()

        return result

    @staticmethod
    def from_proxy_http_response(
        tx_hash: str, response: Dict[str, Any], process_status: Optional[TransactionStatus] = None
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
    def from_http_response(
        tx_hash: str, response: Dict[str, Any]
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
        result.logs = TransactionLogs.from_http_response(response.get("logs", {}))
        result.raw_response = response

        return result

    def to_dictionary(self) -> Dict[str, Any]:
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


class TransactionInMempool:
    def __init__(self) -> None:
        self.hash: str = ""
        self.receiver: IAddress = EmptyAddress()
        self.sender: IAddress = EmptyAddress()
        self.gas_limit: int = 0
        self.gas_price: int = 0
        self.data: str = ""
        self.nonce: int = 0
        self.value: int = 0

    @staticmethod
    def from_http_response(data: Dict[str, Any]) -> "TransactionInMempool":
        data = data["txFields"]
        transaction = TransactionInMempool()

        transaction.hash = data.get("hash", "")
        sender = data.get("sender", "")
        transaction.sender = Address.new_from_bech32(sender) if sender else EmptyAddress()

        receiver = data.get("receiver", "")
        transaction.receiver = Address.new_from_bech32(receiver) if receiver else EmptyAddress()

        transaction.gas_price = data.get("gasPrice", 0)
        transaction.gas_limit = data.get("gasLimit", 0)

        transaction.nonce = data.get("nonce", 0)
        transaction.value = data.get("value", 0)

        data_field = data.get("data", "")
        transaction.data = base64.b64decode(data_field).decode()

        return transaction

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "txHash": self.hash,
            "sender": self.sender.to_bech32(),
            "receiver": self.receiver.to_bech32(),
            "nonce": self.nonce,
            "value": self.value,
            "gasLimit": self.gas_limit,
            "gasPrice": self.gas_price,
            "data": self.data
        }
