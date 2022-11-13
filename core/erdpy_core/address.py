from typing import Any

from erdpy_core import bech32
from erdpy_core.errors import ErrBadAddress

SC_HEX_PUBKEY_PREFIX = "0" * 16
HRP = "erd"
PUBKEY_LENGTH = 32
PUBKEY_STRING_LENGTH = PUBKEY_LENGTH * 2  # hex-encoded
BECH32_LENGTH = 62


class Address():
    _value_hex: str

    def __init__(self, value: Any):
        self._value_hex = ''

        if not value:
            return

        # Copy-constructor
        if isinstance(value, Address):
            value = value._value_hex

        # We keep a hex-encoded string as the "backing" value
        if len(value) == PUBKEY_LENGTH:
            self._value_hex = value.hex()
        elif len(value) == PUBKEY_STRING_LENGTH:
            self._value_hex = _as_string(value)
        elif len(value) == BECH32_LENGTH:
            self._value_hex = _decode_bech32(value).hex()
        else:
            raise ErrBadAddress(value)

    def hex(self) -> str:
        self._assert_validity()
        return self._value_hex

    def bech32(self) -> str:
        self._assert_validity()
        pubkey = self.pubkey()
        b32 = bech32.bech32_encode(HRP, bech32.convertbits(pubkey, 8, 5))
        assert isinstance(b32, str)
        return b32

    def pubkey(self) -> bytes:
        self._assert_validity()
        pubkey = bytes.fromhex(self._value_hex)
        return pubkey

    def is_contract_address(self):
        return self.hex().startswith(SC_HEX_PUBKEY_PREFIX)

    def _assert_validity(self):
        if self._value_hex == '':
            raise Exception("Empty address")

    def __repr__(self):
        return self.bech32()

    @classmethod
    def zero(cls) -> 'Address':
        return Address("0" * 64)


def _as_string(value: Any):
    if isinstance(value, str):
        return value
    return value.decode("utf-8")


def _decode_bech32(value: Any):
    bech32_string = _as_string(value)
    hrp, value_bytes = bech32.bech32_decode(bech32_string)
    if hrp != HRP:
        raise ErrBadAddress(value)
    decoded_bytes = bech32.convertbits(value_bytes, 5, 8, False)
    return bytearray(decoded_bytes)
