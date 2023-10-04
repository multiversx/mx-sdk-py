from typing import Protocol

import multiversx_sdk_core.proto.transaction_pb2 as ProtoTransaction
from multiversx_sdk_core.address import AddressConverter
from multiversx_sdk_core.constants import TRANSACTION_OPTIONS_TX_GUARDED


class ITransaction(Protocol):
    sender: str
    receiver: str
    gas_limit: int
    chainID: str
    gas_price: int
    nonce: int
    amount: int
    data: bytes
    version: int
    signature: bytes
    options: int
    guardian: str
    guardian_signature: bytes


class ProtoSerializer:
    def serialize_transaction(self, transaction: ITransaction) -> bytes:
        converter = AddressConverter()
        receiver_pubkey = converter.bech32_to_pubkey(transaction.receiver)
        sender_pubkey = converter.bech32_to_pubkey(transaction.sender)

        proto_transaction = ProtoTransaction.Transaction()
        proto_transaction.Nonce = transaction.nonce
        proto_transaction.Value = self.serialize_transaction_value(transaction.amount)
        proto_transaction.RcvAddr = bytes(receiver_pubkey)
        proto_transaction.RcvUserName = b""
        proto_transaction.SndAddr = bytes(sender_pubkey)
        proto_transaction.SndUserName = b""
        proto_transaction.GasPrice = transaction.gas_price
        proto_transaction.GasLimit = transaction.gas_limit
        proto_transaction.Data = transaction.data
        proto_transaction.ChainID = transaction.chainID.encode()
        proto_transaction.Version = transaction.version
        proto_transaction.Signature = transaction.signature

        if transaction.options:
            proto_transaction.Options = transaction.options

        if self._is_guarded_transaction(transaction):
            guardian_address = transaction.guardian
            proto_transaction.GuardAddr = converter.bech32_to_pubkey(guardian_address)
            proto_transaction.GuardSignature = transaction.guardian_signature

        encoded_tx: bytes = proto_transaction.SerializeToString()

        return encoded_tx

    def _is_guarded_transaction(self, transaction: ITransaction) -> bool:
        has_guardian = len(transaction.guardian) > 0
        has_guardian_signature = len(transaction.guardian_signature) > 0
        has_options_for_guarded_tx = self._check_tx_options_for_guardian(transaction.options)
        return has_guardian and has_guardian_signature and has_options_for_guarded_tx

    def _check_tx_options_for_guardian(self, options: int) -> bool:
        return (options & TRANSACTION_OPTIONS_TX_GUARDED) == TRANSACTION_OPTIONS_TX_GUARDED

    def serialize_transaction_value(self, tx_value: int):
        if tx_value == 0:
            return bytes([0, 0])

        buffer = self._big_int_to_buffer(tx_value)
        buffer = bytes([0x00]) + buffer

        return buffer

    # this function is implemented to mimic the mx-sdk-js-core implementation
    def _big_int_to_buffer(self, value: int):
        hex_value = self._get_hex_magnitude_of_big_int(value)
        return bytes.fromhex(hex_value)

    def _get_hex_magnitude_of_big_int(self, value: int):
        if value == 0:
            return ""

        if value < 0:
            value = -value

        return self._number_to_padded_hex(value)

    def _number_to_padded_hex(self, value: int):
        hex_value = hex(value)[2:]
        return self._zero_pad_string_if_odd_length(hex_value)

    def _zero_pad_string_if_odd_length(self, input: str):
        return "0" + input if len(input) % 2 else input
