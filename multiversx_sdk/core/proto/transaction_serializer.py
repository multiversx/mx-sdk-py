import multiversx_sdk.core.proto.transaction_pb2 as ProtoTransaction
from multiversx_sdk.core.codec import encode_unsigned_number
from multiversx_sdk.core.transaction import Transaction


class ProtoSerializer:
    def __init__(self) -> None:
        pass

    def serialize_transaction(self, transaction: Transaction) -> bytes:
        proto_transaction = self.convert_to_proto_message(transaction)
        return proto_transaction.SerializeToString()

    def serialize_transaction_value(self, tx_value: int):
        if tx_value == 0:
            return bytes([0, 0])

        buffer = encode_unsigned_number(tx_value)
        buffer = bytes([0x00]) + buffer

        return buffer

    def convert_to_proto_message(self, transaction: Transaction) -> ProtoTransaction.Transaction:
        receiver_pubkey = transaction.receiver.get_public_key()
        sender_pubkey = transaction.sender.get_public_key()

        proto_transaction = ProtoTransaction.Transaction()
        proto_transaction.Nonce = transaction.nonce
        proto_transaction.Value = self.serialize_transaction_value(transaction.value)
        proto_transaction.RcvAddr = receiver_pubkey
        proto_transaction.RcvUserName = transaction.receiver_username.encode()
        proto_transaction.SndAddr = sender_pubkey
        proto_transaction.SndUserName = transaction.sender_username.encode()
        proto_transaction.GasPrice = transaction.gas_price
        proto_transaction.GasLimit = transaction.gas_limit
        proto_transaction.Data = transaction.data
        proto_transaction.ChainID = transaction.chain_id.encode()
        proto_transaction.Version = transaction.version
        proto_transaction.Signature = transaction.signature
        proto_transaction.Options = transaction.options

        if transaction.guardian:
            guardian_address = transaction.guardian
            proto_transaction.GuardAddr = guardian_address.get_public_key()
            proto_transaction.GuardSignature = transaction.guardian_signature

        return proto_transaction
