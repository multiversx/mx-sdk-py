from Cryptodome.Hash import keccak

from multiversx_sdk_core.interfaces import ISignature


class MessageV1:
    """
    Also see: 
     - https://github.com/multiversx/mx-sdk-js-core/blob/v11.2.0/src/signableMessage.ts
     - https://eips.ethereum.org/EIPS/eip-712 (in the past, it served as a basis for the implementation)
    """

    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.signature: ISignature = bytes()

    @classmethod
    def from_string(cls, data: str) -> 'MessageV1':
        return MessageV1(data.encode())

    def serialize_for_signing(self) -> bytes:
        PREFIX = bytes.fromhex("17456c726f6e64205369676e6564204d6573736167653a0a")
        size = str(len(self.data)).encode()
        content = PREFIX + size + self.data
        content_hash = keccak.new(digest_bits=256).update(content).digest()

        return content_hash


class ArbitraryMessage:
    """
    IMPORTANT: this should be rarely used in practice. 

    For signing messages with a regular user wallet, use MessageV1, instead.

    This type of messages allows one to sign arbitrary data.
    It's sometimes used to sign data with a validator wallet (e.g. for composing the "data" field of staking transactions).
    """

    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.signature: ISignature = bytes()

    @classmethod
    def from_string(cls, data: str) -> 'ArbitraryMessage':
        return cls(data.encode())

    def serialize_for_signing(self) -> bytes:
        return self.data
