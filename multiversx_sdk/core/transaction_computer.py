import json
from base64 import b64encode
from collections import OrderedDict
from hashlib import blake2b
from typing import Any

from Cryptodome.Hash import keccak

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import (
    DIGEST_SIZE,
    HEX_ADDRESS_LENGTH,
    MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS,
    TRANSACTION_OPTIONS_TX_GUARDED,
    TRANSACTION_OPTIONS_TX_HASH_SIGN,
)
from multiversx_sdk.core.errors import BadUsageError, NotEnoughGasError
from multiversx_sdk.core.interfaces import INetworkConfig
from multiversx_sdk.core.proto.transaction_serializer import ProtoSerializer
from multiversx_sdk.core.transaction import Transaction


class TransactionComputer:
    def __init__(self) -> None:
        pass

    def compute_transaction_fee(self, transaction: Transaction, network_config: INetworkConfig) -> int:
        """`TransactionsFactoryConfig` can be used here as the `network_config`."""
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

    def compute_bytes_for_signing(self, transaction: Transaction, ignore_options: bool = False) -> bytes:
        """If `ignore_options == False`, the method computes the bytes for signing based on the `version` and `options` of the transaction.
        If the least significant bit of the `options` is set, will serialize transaction for hash signing.

        If `ignore_options == True`, the transaction is simply serialized."""
        self._ensure_fields(transaction)

        dictionary = self._to_dictionary(transaction)
        serialized = self._dict_to_json(dictionary)

        if ignore_options:
            return serialized

        if not self.has_options_set_for_hash_signing(transaction):
            return serialized

        if not transaction.version >= MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS:
            raise Exception("The transaction version you have set does not allow `options`.")

        return keccak.new(digest_bits=256).update(serialized).digest()

    def compute_bytes_for_verifying(self, transaction: Transaction) -> bytes:
        is_signed_by_hash = self.has_options_set_for_hash_signing(transaction)

        if is_signed_by_hash:
            return self.compute_hash_for_signing(transaction)

        return self.compute_bytes_for_signing(transaction)

    def compute_hash_for_signing(self, transaction: Transaction) -> bytes:
        self._ensure_fields(transaction)

        if not self.has_options_set_for_hash_signing(transaction):
            raise Exception(
                "`options` property is not set for hash signing. Please set the least signinficant bit of the `options` property to `1`."
            )

        dictionary = self._to_dictionary(transaction)
        serialized = self._dict_to_json(dictionary)
        return keccak.new(digest_bits=256).update(serialized).digest()

    def compute_transaction_hash(self, transaction: Transaction) -> bytes:
        proto = ProtoSerializer()
        serialized_tx = proto.serialize_transaction(transaction)
        tx_hash = blake2b(serialized_tx, digest_size=DIGEST_SIZE).hexdigest()
        return bytes.fromhex(tx_hash)

    def has_options_set_for_guarded_transaction(self, transaction: Transaction) -> bool:
        return (transaction.options & TRANSACTION_OPTIONS_TX_GUARDED) == TRANSACTION_OPTIONS_TX_GUARDED

    def has_options_set_for_hash_signing(self, transaction: Transaction) -> bool:
        return (transaction.options & TRANSACTION_OPTIONS_TX_HASH_SIGN) == TRANSACTION_OPTIONS_TX_HASH_SIGN

    def apply_guardian(self, transaction: Transaction, guardian: Address) -> None:
        if transaction.version < MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS:
            transaction.version = MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS

        transaction.options = transaction.options | TRANSACTION_OPTIONS_TX_GUARDED
        transaction.guardian = guardian

    def apply_options_for_hash_signing(self, transaction: Transaction) -> None:
        if transaction.version < MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS:
            transaction.version = MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS

        transaction.options = transaction.options | TRANSACTION_OPTIONS_TX_HASH_SIGN

    def is_relayed_v3_transaction(self, transaction: Transaction) -> bool:
        if transaction.relayer and not transaction.relayer.is_empty():
            return True
        return False

    def _ensure_fields(self, transaction: Transaction) -> None:
        if len(transaction.sender.to_hex()) != HEX_ADDRESS_LENGTH:
            raise BadUsageError("Invalid `sender` field. Should be the bech32 address of the sender.")

        if len(transaction.receiver.to_hex()) != HEX_ADDRESS_LENGTH:
            raise BadUsageError("Invalid `receiver` field. Should be the bech32 address of the receiver.")

        if not len(transaction.chain_id):
            raise BadUsageError("The `chainID` field is not set")

        if transaction.version < MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS:
            if self.has_options_set_for_guarded_transaction(transaction) or self.has_options_set_for_hash_signing(
                transaction
            ):
                raise BadUsageError(
                    f"Non-empty transaction options requires transaction version >= {MIN_TRANSACTION_VERSION_THAT_SUPPORTS_OPTIONS}"
                )

    def _to_dictionary(self, transaction: Transaction, with_signature: bool = False) -> dict[str, Any]:
        """Only used when serializing transaction for signing. Internal use only."""
        dictionary: dict[str, Any] = OrderedDict()
        dictionary["nonce"] = transaction.nonce
        dictionary["value"] = str(transaction.value)

        dictionary["receiver"] = transaction.receiver.to_bech32()
        dictionary["sender"] = transaction.sender.to_bech32()

        if transaction.sender_username:
            dictionary["senderUsername"] = b64encode(transaction.sender_username.encode()).decode()

        if transaction.receiver_username:
            dictionary["receiverUsername"] = b64encode(transaction.receiver_username.encode()).decode()

        dictionary["gasPrice"] = transaction.gas_price
        dictionary["gasLimit"] = transaction.gas_limit

        if transaction.data:
            dictionary["data"] = b64encode(transaction.data).decode()

        if with_signature:
            if transaction.signature:
                dictionary["signature"] = transaction.signature.hex()

        dictionary["chainID"] = transaction.chain_id

        if transaction.version:
            dictionary["version"] = transaction.version

        if transaction.options:
            dictionary["options"] = transaction.options

        if transaction.guardian:
            dictionary["guardian"] = transaction.guardian.to_bech32()

        if transaction.relayer:
            dictionary["relayer"] = transaction.relayer.to_bech32()

        return dictionary

    def _dict_to_json(self, dictionary: dict[str, Any]) -> bytes:
        return json.dumps(dictionary, separators=(",", ":")).encode("utf-8")
