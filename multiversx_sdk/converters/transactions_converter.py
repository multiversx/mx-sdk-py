import base64
from typing import Any, Dict, Union

from multiversx_sdk.converters.errors import MissingFieldError
from multiversx_sdk.core.interfaces import ITransaction
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_outcome_parsers.resources import (
    SmartContractResult, TransactionEvent, TransactionLogs, TransactionOutcome)
from multiversx_sdk.network_providers.contract_results import \
    ContractResultItem as SCResultItemOnNetwork
from multiversx_sdk.network_providers.transaction_events import \
    TransactionEvent as TransactionEventOnNetwork
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork


class TransactionsConverter:
    def __init__(self) -> None:
        pass

    def transaction_to_dictionary(self, transaction: ITransaction) -> Dict[str, Any]:
        return {
            "nonce": transaction.nonce,
            "value": str(transaction.value),
            "receiver": transaction.receiver,
            "sender": transaction.sender,
            "senderUsername": self._value_to_b64_or_empty(transaction.sender_username),
            "receiverUsername": self._value_to_b64_or_empty(transaction.receiver_username),
            "gasPrice": transaction.gas_price,
            "gasLimit": transaction.gas_limit,
            "data": self._value_to_b64_or_empty(transaction.data),
            "chainID": transaction.chain_id,
            "version": transaction.version,
            "options": transaction.options,
            "guardian": transaction.guardian,
            "signature": self._value_to_hex_or_empty(transaction.signature),
            "guardianSignature": self._value_to_hex_or_empty(transaction.guardian_signature),
            "relayer": transaction.relayer,
            "innerTransactions": [self.transaction_to_dictionary(inner_tx) for inner_tx in transaction.inner_transactions]
        }

    def dictionary_to_transaction(self, dictionary: Dict[str, Any]) -> Transaction:
        self._ensure_mandatory_fields_for_transaction(dictionary)

        return Transaction(
            nonce=dictionary.get("nonce", None),
            value=int(dictionary.get("value", None)),
            receiver=dictionary["receiver"],
            receiver_username=self._bytes_from_b64(dictionary.get("receiverUsername", "")).decode(),
            sender=dictionary["sender"],
            sender_username=self._bytes_from_b64(dictionary.get("senderUsername", "")).decode(),
            guardian=dictionary.get("guardian", None),
            gas_price=dictionary.get("gasPrice", None),
            gas_limit=dictionary["gasLimit"],
            data=self._bytes_from_b64(dictionary.get("data", "")),
            chain_id=dictionary["chainID"],
            version=dictionary.get("version", None),
            options=dictionary.get("options", None),
            signature=self._bytes_from_hex(dictionary.get("signature", "")),
            guardian_signature=self._bytes_from_hex(dictionary.get("guardianSignature", "")),
            relayer=dictionary.get("relayer", None),
            inner_transactions=[self.dictionary_to_transaction(inner_tx) for inner_tx in dictionary.get("innerTransactions", [])],
        )

    def transaction_on_network_to_outcome(self, transaction_on_network: TransactionOnNetwork) -> TransactionOutcome:
        results = [self._sc_result_item_on_network_to_sc_result(item) for item in transaction_on_network.contract_results.items]
        logs = TransactionLogs(
            address=transaction_on_network.logs.address.to_bech32(),
            events=[self._event_on_network_to_event(event) for event in transaction_on_network.logs.events]
        )

        return TransactionOutcome(
            transaction_results=results,
            transaction_logs=logs
        )

    def _event_on_network_to_event(self, event: TransactionEventOnNetwork) -> TransactionEvent:
        address = event.address.to_bech32()
        identifier = event.identifier
        topics = [topic.raw for topic in event.topics]

        legacy_data = event.data_payload.raw if event.data_payload else b'' or event.data.encode()
        data_items = [data.raw for data in event.additional_data] if event.additional_data else []

        if len(data_items) == 0:
            if len(legacy_data):
                data_items.append(legacy_data)

        return TransactionEvent(address, identifier, topics, data_items)

    def _sc_result_item_on_network_to_sc_result(self, sc_result_item: SCResultItemOnNetwork) -> SmartContractResult:
        sender = sc_result_item.sender.to_bech32()
        receiver = sc_result_item.receiver.to_bech32()
        data = sc_result_item.data.encode()
        logs = TransactionLogs(
            address=sc_result_item.logs.address.to_bech32(),
            events=[self._event_on_network_to_event(event) for event in sc_result_item.logs.events]
        )

        return SmartContractResult(
            sender=sender,
            receiver=receiver,
            data=data,
            logs=logs
        )

    def _ensure_mandatory_fields_for_transaction(self, dictionary: Dict[str, Any]) -> None:
        sender = dictionary.get("sender", None)
        if sender is None:
            raise MissingFieldError("The 'sender' key is missing from the dictionary")

        receiver = dictionary.get("receiver", None)
        if receiver is None:
            raise MissingFieldError("The 'receiver' key is missing from the dictionary")

        chain_id = dictionary.get("chainID", None)
        if chain_id is None:
            raise MissingFieldError("The 'chainID' key is missing from the dictionary")

        gas_limit = dictionary.get("gasLimit", None)
        if gas_limit is None:
            raise MissingFieldError("The 'gasLimit' key is missing from the dictionary")

    def _value_to_b64_or_empty(self, value: Union[str, bytes]) -> str:
        value_as_bytes = value.encode() if isinstance(value, str) else value

        if len(value):
            return base64.b64encode(value_as_bytes).decode()
        return ""

    def _value_to_hex_or_empty(self, value: bytes) -> str:
        if len(value):
            return value.hex()
        return ""

    def _bytes_from_b64(self, value: str) -> bytes:
        if len(value):
            return base64.b64decode(value.encode())
        return b""

    def _bytes_from_hex(self, value: str) -> bytes:
        if len(value):
            return bytes.fromhex(value)
        return b""
