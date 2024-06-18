import io
from typing import Any, Protocol

from multiversx_sdk.abi.shared import read_bytes_exactly
from multiversx_sdk.core.address import PUBKEY_LENGTH


class IAddress(Protocol):
    """
    For internal use only.
    """

    def get_public_key(self) -> bytes:
        ...


class AddressValue:
    def __init__(self, value: bytes = b"") -> None:
        self.value = value

    @classmethod
    def from_address(cls, address: IAddress) -> "AddressValue":
        return cls(address.get_public_key())

    def encode_nested(self, writer: io.BytesIO):
        self._check_pub_key_length(self.value)
        writer.write(self.value)

    def encode_top_level(self, writer: io.BytesIO):
        self.encode_nested(writer)

    def decode_nested(self, reader: io.BytesIO):
        data = read_bytes_exactly(reader, PUBKEY_LENGTH)
        self.value = data

    def decode_top_level(self, data: bytes):
        self._check_pub_key_length(data)
        self.value = data

    def _check_pub_key_length(self, pubkey: bytes) -> None:
        if len(pubkey) != PUBKEY_LENGTH:
            raise ValueError(f"public key (address) has invalid length: {len(pubkey)}")

    def set_payload(self, value: Any):
        pubkey = bytes(value)
        self._check_pub_key_length(pubkey)
        self.value = pubkey

    def get_payload(self) -> Any:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AddressValue) and self.value == other.value

    def __bytes__(self) -> bytes:
        return self.value
