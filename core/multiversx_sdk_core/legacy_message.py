from Cryptodome.Hash import keccak

from multiversx_sdk_core.interfaces import ISignature


class LegacyMessage:
    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.signature: ISignature = bytes()

    @classmethod
    def from_string(cls, data: str) -> 'LegacyMessage':
        return LegacyMessage(data.encode())

    def serialize_for_signing(self) -> bytes:
        LEGACY_MESSAGE_PREFIX = bytes.fromhex("17456c726f6e64205369676e6564204d6573736167653a0a")
        size = str(len(self.data)).encode()
        content = LEGACY_MESSAGE_PREFIX + size + self.data
        content_hash = keccak.new(digest_bits=256).update(content).digest()

        return content_hash
