import json
from base64 import b64encode
from collections import OrderedDict
from hashlib import blake2b
from typing import Any, Dict, Optional, Protocol

from multiversx_sdk_core.constants import (DEFAULT_HRP, DIGEST_SIZE,
                                           TRANSACTION_MIN_GAS_PRICE,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT)
from multiversx_sdk_core.errors import NotEnoughGasError
from multiversx_sdk_core.interfaces import INetworkConfig, ITransaction
from multiversx_sdk_core.proto.transaction_serializer import ProtoSerializer


class IAddressConverter(Protocol):
    def __init__(self, hrp: str = DEFAULT_HRP) -> None:
        ...

    def bech32_to_pubkey(self, value: str) -> bytes:
        ...

    def pubkey_to_bech32(self, pubkey: bytes) -> str:
        ...


class Transaction:
    def __init__(self,
                 sender: str,
                 receiver: str,
                 gas_limit: int,
                 chain_id: str,
                 nonce: Optional[int] = None,
                 value: Optional[int] = None,
                 sender_username: Optional[str] = None,
                 receiver_username: Optional[str] = None,
                 gas_price: Optional[int] = None,
                 data: Optional[bytes] = None,
                 version: Optional[int] = None,
                 options: Optional[int] = None,
                 guardian: Optional[str] = None,
                 signature: Optional[bytes] = None,
                 guardian_signature: Optional[bytes] = None
                 ) -> None:
        self.chain_id = chain_id
        self.sender = sender
        self.receiver = receiver
        self.gas_limit = gas_limit

        self.nonce = nonce or 0
        self.value = value or 0
        self.data = data or bytes()
        self.signature = signature or bytes()

        self.sender_username = sender_username or ""
        self.receiver_username = receiver_username or ""

        self.gas_price = gas_price or TRANSACTION_MIN_GAS_PRICE
        self.version = version or TRANSACTION_VERSION_DEFAULT
        self.options = options or TRANSACTION_OPTIONS_DEFAULT

        self.guardian = guardian or ""
        self.guardian_signature = guardian_signature or bytes()


class TransactionComputer:
    def __init__(self) -> None:
        pass

    def compute_transaction_fee(self, transaction: ITransaction, network_config: INetworkConfig) -> int:
        move_balance_gas = network_config.min_gas_limit + len(transaction.data) * network_config.gas_per_data_byte
        if move_balance_gas > transaction.gas_limit:
            raise NotEnoughGasError(transaction.gas_limit)

        fee_for_move = move_balance_gas * transaction.gas_price
        if move_balance_gas == transaction.gas_limit:
            return int(fee_for_move)

        diff = transaction.gas_limit - move_balance_gas
        modified_gas_price = transaction.gas_price * network_config.gas_price_modifier
        processing_fee = diff * modified_gas_price

        return int(fee_for_move + processing_fee)

    def compute_bytes_for_signing(self, transaction: ITransaction) -> bytes:
        dictionary = self._to_dictionary(transaction)
        serialized = self._dict_to_json(dictionary)
        return serialized

    def compute_transaction_hash(self, transaction: ITransaction) -> bytes:
        proto = ProtoSerializer()
        serialized_tx = proto.serialize_transaction(transaction)
        tx_hash = blake2b(serialized_tx, digest_size=DIGEST_SIZE).hexdigest()
        return bytes.fromhex(tx_hash)

    def _to_dictionary(self, transaction: ITransaction) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["nonce"] = transaction.nonce
        dictionary["value"] = str(transaction.value)

        dictionary["receiver"] = transaction.receiver
        dictionary["sender"] = transaction.sender

        if transaction.sender_username:
            dictionary["senderUsername"] = b64encode(transaction.sender_username.encode()).decode()

        if transaction.receiver_username:
            dictionary["receiverUsername"] = b64encode(transaction.receiver_username.encode()).decode()

        dictionary["gasPrice"] = transaction.gas_price
        dictionary["gasLimit"] = transaction.gas_limit

        if transaction.data:
            dictionary["data"] = b64encode(transaction.data).decode()

        dictionary["chainID"] = transaction.chain_id

        if transaction.version:
            dictionary["version"] = transaction.version

        if transaction.options:
            dictionary["options"] = transaction.options

        if transaction.guardian:
            dictionary["guardian"] = transaction.guardian

        return dictionary

    def _dict_to_json(self, dictionary: Dict[str, Any]) -> bytes:
        serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf-8")
        return serialized
