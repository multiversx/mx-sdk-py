import base64
from typing import Any, Dict, Protocol

from multiversx_sdk.core.address import Address, EmptyAddress
from multiversx_sdk.network_providers.interface import IAddress


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
