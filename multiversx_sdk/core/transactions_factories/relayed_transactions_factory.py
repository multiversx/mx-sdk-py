import base64
import json
from typing import Any, Dict, List, Protocol, Sequence

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import InvalidInnerTransactionError
from multiversx_sdk.core.interfaces import IAddress, ITransaction
from multiversx_sdk.core.serializer import args_to_string
from multiversx_sdk.core.transaction import Transaction


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int


class RelayedTransactionsFactory:
    def __init__(self, config: IConfig) -> None:
        self._config = config

    def create_relayed_v1_transaction(self,
                                      inner_transaction: ITransaction,
                                      relayer_address: IAddress) -> Transaction:
        if not inner_transaction.gas_limit:
            raise InvalidInnerTransactionError("The gas limit is not set for the inner transaction")

        if not inner_transaction.signature:
            raise InvalidInnerTransactionError("The inner transaction is not signed")

        serialized_transaction = self._prepare_inner_transaction_for_relayed_v1(inner_transaction)
        data = f"relayedTx@{serialized_transaction.encode().hex()}"

        gas_limit = self._config.min_gas_limit + self._config.gas_limit_per_byte * len(data) + inner_transaction.gas_limit

        return Transaction(
            chain_id=self._config.chain_id,
            sender=relayer_address.to_bech32(),
            receiver=inner_transaction.sender,
            gas_limit=gas_limit,
            data=data.encode()
        )

    def create_relayed_v2_transaction(self,
                                      inner_transaction: ITransaction,
                                      inner_transaction_gas_limit: int,
                                      relayer_address: IAddress) -> Transaction:
        if inner_transaction.gas_limit:
            raise InvalidInnerTransactionError("The gas limit should not be set for the inner transaction")

        if not inner_transaction.signature:
            raise InvalidInnerTransactionError("The inner transaction is not signed")

        arguments: List[Any] = [
            Address.new_from_bech32(inner_transaction.receiver),
            inner_transaction.nonce,
            inner_transaction.data,
            inner_transaction.signature
        ]

        data = f"relayedTxV2@{args_to_string(arguments)}"
        gas_limit = inner_transaction_gas_limit + self._config.min_gas_limit + self._config.gas_limit_per_byte * len(data)

        return Transaction(
            sender=relayer_address.to_bech32(),
            receiver=inner_transaction.sender,
            value=0,
            gas_limit=gas_limit,
            chain_id=self._config.chain_id,
            data=data.encode(),
            version=inner_transaction.version,
            options=inner_transaction.options
        )

    def create_relayed_v3_transaction(self,
                                      relayer_address: IAddress,
                                      inner_transactions: Sequence[ITransaction]) -> Transaction:
        if len(inner_transactions) == 0:
            raise InvalidInnerTransactionError("The are no inner transactions")

        inner_txs_gas_limit = 0
        for inner_transaction in inner_transactions:
            if not inner_transaction.signature:
                raise InvalidInnerTransactionError("The inner transaction is not signed")

            if inner_transaction.relayer != relayer_address.to_bech32():
                raise InvalidInnerTransactionError("The inner transaction has an incorrect relayer address")

            inner_txs_gas_limit += inner_transaction.gas_limit

        move_balances_gas = self._config.min_gas_limit * len(inner_transactions)
        gas_limit = move_balances_gas + inner_txs_gas_limit

        return Transaction(
            sender=relayer_address.to_bech32(),
            receiver=relayer_address.to_bech32(),
            value=0,
            gas_limit=gas_limit,
            chain_id=self._config.chain_id,
            inner_transactions=inner_transactions,
        )

    def _prepare_inner_transaction_for_relayed_v1(self, inner_transaction: ITransaction) -> str:
        sender = Address.new_from_bech32(inner_transaction.sender).to_hex()
        receiver = Address.new_from_bech32(inner_transaction.receiver).to_hex()

        tx: Dict[str, Any] = {
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
            guardian = Address.new_from_bech32(inner_transaction.guardian).to_hex()
            tx["guardian"] = base64.b64encode(bytes.fromhex(guardian)).decode()

        if inner_transaction.guardian_signature:
            tx["guardianSignature"] = base64.b64encode(inner_transaction.guardian_signature).decode()

        if inner_transaction.sender_username:
            tx["sndUserName"] = base64.b64encode(inner_transaction.sender_username.encode()).decode()

        if inner_transaction.receiver_username:
            tx["rcvUserName"] = base64.b64encode(inner_transaction.receiver_username.encode()).decode()

        return json.dumps(tx, separators=(",", ":"))
