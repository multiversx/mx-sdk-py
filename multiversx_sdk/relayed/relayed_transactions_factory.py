import base64
import json
import logging
from typing import Any

from multiversx_sdk.abi import AddressValue, BigUIntValue, Serializer
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.core import Address, Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.relayed.errors import InvalidInnerTransactionError

logger = logging.getLogger("relayed_transactions_factory")


class RelayedTransactionsFactory:
    """
    The Relayed Transactions V1 and V2 will soon be deprecated from the network. Please use Relayed Transactions V3 instead.
    The transactions are created from the perspective of the relayer. The 'sender' represents the relayer.
    """

    def __init__(self, config: TransactionsFactoryConfig) -> None:
        logger.warning("RelayedTransactionsFactory is deprecated. Please use Relayed Transactions V3 instead.")
        self._config = config

    def create_relayed_v1_transaction(self, inner_transaction: Transaction, relayer_address: Address) -> Transaction:
        if not inner_transaction.gas_limit:
            raise InvalidInnerTransactionError("The gas limit is not set for the inner transaction")

        if not inner_transaction.signature:
            raise InvalidInnerTransactionError("The inner transaction is not signed")

        serialized_transaction = self._prepare_inner_transaction_for_relayed_v1(inner_transaction)
        data = f"relayedTx@{serialized_transaction.encode().hex()}"

        gas_limit = (
            self._config.min_gas_limit + self._config.gas_limit_per_byte * len(data) + inner_transaction.gas_limit
        )

        return Transaction(
            chain_id=self._config.chain_id,
            sender=relayer_address,
            receiver=inner_transaction.sender,
            gas_limit=gas_limit,
            data=data.encode(),
        )

    def create_relayed_v2_transaction(
        self,
        inner_transaction: Transaction,
        inner_transaction_gas_limit: int,
        relayer_address: Address,
    ) -> Transaction:
        if inner_transaction.gas_limit:
            raise InvalidInnerTransactionError("The gas limit should not be set for the inner transaction")

        if not inner_transaction.signature:
            raise InvalidInnerTransactionError("The inner transaction is not signed")

        arguments: list[Any] = [
            AddressValue.new_from_address(inner_transaction.receiver),
            BigUIntValue(inner_transaction.nonce),
            BytesValue(inner_transaction.data),
            BytesValue(inner_transaction.signature),
        ]

        serializer = Serializer()
        data = f"relayedTxV2@{serializer.serialize(arguments)}"
        gas_limit = (
            inner_transaction_gas_limit + self._config.min_gas_limit + self._config.gas_limit_per_byte * len(data)
        )

        return Transaction(
            sender=relayer_address,
            receiver=inner_transaction.sender,
            value=0,
            gas_limit=gas_limit,
            chain_id=self._config.chain_id,
            data=data.encode(),
            version=inner_transaction.version,
            options=inner_transaction.options,
        )

    def _prepare_inner_transaction_for_relayed_v1(self, inner_transaction: Transaction) -> str:
        sender = inner_transaction.sender.to_hex()
        receiver = inner_transaction.receiver.to_hex()

        tx: dict[str, Any] = {
            "nonce": inner_transaction.nonce,
            "sender": base64.b64encode(bytes.fromhex(sender)).decode(),
            "receiver": base64.b64encode(bytes.fromhex(receiver)).decode(),
            "value": inner_transaction.value,
            "gasPrice": inner_transaction.gas_price,
            "gasLimit": inner_transaction.gas_limit,
            "data": base64.b64encode(inner_transaction.data).decode(),
            "signature": base64.b64encode(inner_transaction.signature).decode(),
            "chainID": base64.b64encode(inner_transaction.chain_id.encode()).decode(),
            "version": inner_transaction.version,
        }

        if inner_transaction.options:
            tx["options"] = inner_transaction.options

        if inner_transaction.guardian:
            guardian = inner_transaction.guardian.to_hex()
            tx["guardian"] = base64.b64encode(bytes.fromhex(guardian)).decode()

        if inner_transaction.guardian_signature:
            tx["guardianSignature"] = base64.b64encode(inner_transaction.guardian_signature).decode()

        if inner_transaction.sender_username:
            tx["sndUserName"] = base64.b64encode(inner_transaction.sender_username.encode()).decode()

        if inner_transaction.receiver_username:
            tx["rcvUserName"] = base64.b64encode(inner_transaction.receiver_username.encode()).decode()

        return json.dumps(tx, separators=(",", ":"))
