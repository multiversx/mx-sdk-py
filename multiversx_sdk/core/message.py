from typing import Any, Dict, Optional

from Cryptodome.Hash import keccak

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import (
    DEFAULT_MESSAGE_VERSION,
    SDK_PY_SIGNER,
    UNKNOWN_SIGNER,
)


class Message:
    def __init__(
        self,
        data: bytes,
        signature: bytes = b"",
        address: Optional[Address] = None,
        version: int = DEFAULT_MESSAGE_VERSION,
        signer: str = SDK_PY_SIGNER,
    ) -> None:
        self.data = data
        self.signature = signature
        self.address = address
        self.version = version
        self.signer = signer


class MessageComputer:
    """
    Also see:
     - https://github.com/multiversx/mx-sdk-js-core/blob/v11.2.0/src/signableMessage.ts
     - https://eips.ethereum.org/EIPS/eip-712 (in the past, it served as a basis for the implementation)
    """

    def __init__(self) -> None:
        pass

    def compute_bytes_for_signing(self, message: Message) -> bytes:
        PREFIX = bytes.fromhex("17456c726f6e64205369676e6564204d6573736167653a0a")
        size = str(len(message.data)).encode()
        content = PREFIX + size + message.data
        content_hash = keccak.new(digest_bits=256).update(content).digest()

        return content_hash

    def compute_bytes_for_verifying(self, message: Message) -> bytes:
        return self.compute_bytes_for_signing(message)

    def pack_message(self, message: Message) -> Dict[str, Any]:
        return {
            "address": message.address.to_bech32() if message.address else "",
            "message": message.data.hex(),
            "signature": message.signature.hex(),
            "version": message.version,
            "signer": message.signer,
        }

    def unpack_message(self, packed_message: Dict[str, Any]) -> Message:
        data = packed_message.get("message", "")
        data = self._trim_hex_prefix(data)

        signature = packed_message.get("signature", "")
        signature = self._trim_hex_prefix(signature)

        address = packed_message.get("address", "")
        address = Address.from_bech32(address) if address else None

        version = packed_message.get("version", DEFAULT_MESSAGE_VERSION)
        signer = packed_message.get("signer", UNKNOWN_SIGNER)

        return Message(
            data=bytes.fromhex(data),
            address=address,
            signature=bytes.fromhex(signature),
            version=version,
            signer=signer,
        )

    def _trim_hex_prefix(self, data: str) -> str:
        if data.startswith("0x") or data.startswith("0X"):
            return data[2:]
        return data
