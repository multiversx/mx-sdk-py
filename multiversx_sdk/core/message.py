from typing import Any, Dict

from Cryptodome.Hash import keccak

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.interfaces import IAddress, IMessage


class Message:
    def __init__(self, data: bytes, address: IAddress, signature: bytes = b"", version: int = 1) -> None:
        self.data = data
        self.signature = signature
        self.address = address
        self.version = version


class MessageComputer:
    """
    Also see:
     - https://github.com/multiversx/mx-sdk-js-core/blob/v11.2.0/src/signableMessage.ts
     - https://eips.ethereum.org/EIPS/eip-712 (in the past, it served as a basis for the implementation)
    """

    def __init__(self) -> None:
        pass

    def compute_bytes_for_signing(self, message: IMessage) -> bytes:
        PREFIX = bytes.fromhex("17456c726f6e64205369676e6564204d6573736167653a0a")
        size = str(len(message.data)).encode()
        content = PREFIX + size + message.data
        content_hash = keccak.new(digest_bits=256).update(content).digest()

        return content_hash

    def compute_bytes_for_verifying(self, message: IMessage) -> bytes:
        return self.compute_bytes_for_signing(message)

    def pack(self, message: IMessage) -> Dict[str, Any]:
        return {
            "address": message.address.to_bech32(),
            "message": message.data.hex(),
            "signature": message.signature.hex(),
            "version": message.version
        }

    def unpack(self, packed_message: Dict[str, Any]) -> Message:
        data: str = packed_message["message"]
        if data.startswith("0x") or data.startswith("0X"):
            data = data[2:]

        signature: str = packed_message["signature"]
        if signature.startswith("0x") or signature.startswith("0X"):
            signature = signature[2:]

        address = Address.from_bech32(packed_message["address"])
        version = packed_message["version"]

        return Message(
            data=bytes.fromhex(data),
            address=address,
            signature=bytes.fromhex(signature),
            version=version
        )
