from typing import Protocol

import multiversx_sdk_core.proto.transaction_pb2 as ProtoTransaction
from multiversx_sdk_core.codec import encode_unsigned_number
from multiversx_sdk_core.constants import (DEFAULT_HRP,
                                           TRANSACTION_OPTIONS_TX_GUARDED)


class ITransaction(Protocol):
    sender: str
    receiver: str
    gas_limit: int
    chainID: str
    gas_price: int
    sender_username: str
    receiver_username: str
    nonce: int
    amount: int
    data: bytes
    version: int
    signature: bytes
    options: int
    guardian: str
    guardian_signature: bytes


class IAddressConverter(Protocol):
    def __init__(self, hrp: str = DEFAULT_HRP) -> None:
        ...

    def bech32_to_pubkey(self, value: str) -> bytes:
        ...


class ProtoSerializer:
    def __init__(self, converter: IAddressConverter) -> None:
        self.address_converter = converter

    def serialize_transaction(self, transaction: ITransaction) -> bytes:
        receiver_pubkey = self.address_converter.bech32_to_pubkey(transaction.receiver)
        sender_pubkey = self.address_converter.bech32_to_pubkey(transaction.sender)

        proto_transaction = ProtoTransaction.Transaction()
        proto_transaction.Nonce = transaction.nonce
        proto_transaction.Value = self.serialize_transaction_value(transaction.amount)
        proto_transaction.RcvAddr = bytes(receiver_pubkey)
        proto_transaction.RcvUserName = transaction.receiver_username.encode()
        proto_transaction.SndAddr = bytes(sender_pubkey)
        proto_transaction.SndUserName = transaction.sender_username.encode()
        proto_transaction.GasPrice = transaction.gas_price
        proto_transaction.GasLimit = transaction.gas_limit
        proto_transaction.Data = transaction.data
        proto_transaction.ChainID = transaction.chainID.encode()
        proto_transaction.Version = transaction.version
        proto_transaction.Signature = transaction.signature
        proto_transaction.Options = transaction.options

        if self._is_guarded_transaction(transaction):
            guardian_address = transaction.guardian
            proto_transaction.GuardAddr = bytes(self.address_converter.bech32_to_pubkey(guardian_address))
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

        buffer = encode_unsigned_number(tx_value)
        buffer = bytes([0x00]) + buffer

        return buffer
