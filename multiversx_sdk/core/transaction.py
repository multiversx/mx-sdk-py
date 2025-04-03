import base64
from typing import Any, Optional, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import (
    TRANSACTION_MIN_GAS_PRICE,
    TRANSACTION_OPTIONS_DEFAULT,
    TRANSACTION_VERSION_DEFAULT,
)


class Transaction:
    def __init__(
        self,
        sender: Address,
        receiver: Address,
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
        guardian: Optional[Address] = None,
        signature: Optional[bytes] = None,
        guardian_signature: Optional[bytes] = None,
        relayer: Optional[Address] = None,
        relayer_signature: Optional[bytes] = None,
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

        self.guardian = guardian
        self.guardian_signature = guardian_signature or bytes()

        self.relayer = relayer
        self.relayer_signature = relayer_signature or bytes()

    def to_dictionary(self) -> dict[str, Any]:
        return {
            "nonce": self.nonce,
            "value": str(self.value),
            "receiver": self.receiver.to_bech32(),
            "sender": self.sender.to_bech32(),
            "senderUsername": self._value_to_b64_or_empty(self.sender_username),
            "receiverUsername": self._value_to_b64_or_empty(self.receiver_username),
            "gasPrice": self.gas_price,
            "gasLimit": self.gas_limit,
            "data": self._value_to_b64_or_empty(self.data),
            "chainID": self.chain_id,
            "version": self.version,
            "options": self.options,
            "guardian": self.guardian.to_bech32() if self.guardian else "",
            "signature": self._value_to_hex_or_empty(self.signature),
            "guardianSignature": self._value_to_hex_or_empty(self.guardian_signature),
            "relayer": self.relayer.to_bech32() if self.relayer else "",
            "relayerSignature": self._value_to_hex_or_empty(self.relayer_signature),
        }

    @staticmethod
    def new_from_dictionary(dictionary: dict[str, Any]) -> "Transaction":
        _ensure_mandatory_fields_for_transaction(dictionary)

        guardian = dictionary.get("guardian") or None
        if guardian:
            guardian = Address.new_from_bech32(guardian)

        relayer = dictionary.get("relayer") or None
        if relayer:
            relayer = Address.new_from_bech32(relayer)

        value = dictionary.get("value", None)
        value = int(value) if value is not None else None

        return Transaction(
            nonce=dictionary.get("nonce", None),
            value=value,
            receiver=Address.new_from_bech32(dictionary["receiver"]),
            receiver_username=_bytes_from_b64(dictionary.get("receiverUsername", "")).decode(),
            sender=Address.new_from_bech32(dictionary["sender"]),
            sender_username=_bytes_from_b64(dictionary.get("senderUsername", "")).decode(),
            guardian=guardian,
            gas_price=dictionary.get("gasPrice", None),
            gas_limit=dictionary["gasLimit"],
            data=_bytes_from_b64(dictionary.get("data", "")),
            chain_id=dictionary["chainID"],
            version=dictionary.get("version", None),
            options=dictionary.get("options", None),
            signature=_bytes_from_hex(dictionary.get("signature", "")),
            guardian_signature=_bytes_from_hex(dictionary.get("guardianSignature", "")),
            relayer=relayer,
            relayer_signature=_bytes_from_hex(dictionary.get("relayerSignature", "")),
        )

    def _value_to_b64_or_empty(self, value: Union[str, bytes]) -> str:
        value_as_bytes = value.encode() if isinstance(value, str) else value

        if len(value):
            return base64.b64encode(value_as_bytes).decode()
        return ""

    def _value_to_hex_or_empty(self, value: bytes) -> str:
        if len(value):
            return value.hex()
        return ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False

        return self.__dict__ == other.__dict__


def _ensure_mandatory_fields_for_transaction(dictionary: dict[str, Any]) -> None:
    sender = dictionary.get("sender", None)
    if sender is None:
        raise Exception("The 'sender' key is missing from the dictionary")

    receiver = dictionary.get("receiver", None)
    if receiver is None:
        raise Exception("The 'receiver' key is missing from the dictionary")

    chain_id = dictionary.get("chainID", None)
    if chain_id is None:
        raise Exception("The 'chainID' key is missing from the dictionary")

    gas_limit = dictionary.get("gasLimit", None)
    if gas_limit is None:
        raise Exception("The 'gasLimit' key is missing from the dictionary")


def _bytes_from_b64(value: str) -> bytes:
    if len(value):
        return base64.b64decode(value.encode())
    return b""


def _bytes_from_hex(value: str) -> bytes:
    if len(value):
        return bytes.fromhex(value)
    return b""
