import json
from base64 import b64encode
from collections import OrderedDict
from hashlib import blake2b
from typing import Any, Dict

from Cryptodome.Hash import keccak

from multiversx_sdk.core.constants import (BECH32_ADDRESS_LENGTH, DIGEST_SIZE,
                                           TRANSACTION_OPTIONS_TX_GUARDED,
                                           TRANSACTION_OPTIONS_TX_HASH_SIGN)
from multiversx_sdk.core.errors import BadUsageError, NotEnoughGasError
from multiversx_sdk.core.interfaces import INetworkConfig, ITransaction
from multiversx_sdk.core.proto.transaction_serializer import ProtoSerializer


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
        self._ensure_fields(transaction)

        if transaction.version >= 2 and self.has_options_set_for_hash_signing(transaction):
            return self.compute_hash_for_signing(transaction)

        dictionary = self._to_dictionary(transaction)
        serialized = self._dict_to_json(dictionary)
        return serialized

    def compute_hash_for_signing(self, transaction: ITransaction) -> bytes:
        dictionary = self._to_dictionary(transaction)
        serialized = self._dict_to_json(dictionary)
        return keccak.new(digest_bits=256).update(serialized).digest()

    def compute_transaction_hash(self, transaction: ITransaction) -> bytes:
        proto = ProtoSerializer()
        serialized_tx = proto.serialize_transaction(transaction)
        tx_hash = blake2b(serialized_tx, digest_size=DIGEST_SIZE).hexdigest()
        return bytes.fromhex(tx_hash)

    def has_options_set_for_guarded_transaction(self, transaction: ITransaction) -> bool:
        return (transaction.options & TRANSACTION_OPTIONS_TX_GUARDED) == TRANSACTION_OPTIONS_TX_GUARDED

    def has_options_set_for_hash_signing(self, transaction: ITransaction) -> bool:
        return (transaction.options & TRANSACTION_OPTIONS_TX_HASH_SIGN) == TRANSACTION_OPTIONS_TX_HASH_SIGN

    def apply_guardian(self, transaction: ITransaction, guardian: str) -> None:
        transaction.version = 2
        transaction.options = transaction.options | TRANSACTION_OPTIONS_TX_GUARDED
        transaction.guardian = guardian

    def _ensure_fields(self, transaction: ITransaction) -> None:
        if len(transaction.sender) != BECH32_ADDRESS_LENGTH:
            raise BadUsageError("The `sender` field is invalid. Should be set to the bech32 address of the sender.")

        if len(transaction.receiver) != BECH32_ADDRESS_LENGTH:
            raise BadUsageError("The `receiver` field is invalid. Should be set to the bech32 address of the receiver.")

        if not len(transaction.chain_id):
            raise BadUsageError("The `chainID` field is not set")

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
