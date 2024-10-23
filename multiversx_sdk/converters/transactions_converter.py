import base64
from typing import Any, Dict, Union

from multiversx_sdk.converters.errors import MissingFieldError
from multiversx_sdk.core.interfaces import ITransaction
from multiversx_sdk.core.transaction import Transaction


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
            "guardianSignature": self._value_to_hex_or_empty(transaction.guardian_signature)
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
