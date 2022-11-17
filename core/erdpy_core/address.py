from erdpy_core import bech32
from erdpy_core.errors import ErrBadAddress, ErrBadPubkeyLength

SC_HEX_PUBKEY_PREFIX = "0" * 16
HRP = "erd"
PUBKEY_LENGTH = 32
PUBKEY_STRING_LENGTH = PUBKEY_LENGTH * 2  # hex-encoded
BECH32_LENGTH = 62


class Address():
    def __init__(self, pubkey: bytes):
        if len(pubkey) != PUBKEY_LENGTH:
            raise ErrBadPubkeyLength(len(pubkey), PUBKEY_LENGTH)

        self._pubkey = pubkey

    @classmethod
    def from_bech32(cls, value: str) -> 'Address':
        pubkey = _decode_bech32(value)
        return Address(pubkey)

    @classmethod
    def from_hex(cls, value: str) -> 'Address':
        pubkey = bytes.fromhex(value)
        return Address(pubkey)

    @classmethod
    def zero(cls) -> 'Address':
        return Address(bytearray(32))

    def pubkey(self) -> bytes:
        return self._pubkey

    def hex(self) -> str:
        return self.pubkey().hex()

    def bech32(self) -> str:
        pubkey = self.pubkey()
        converted = bech32.convertbits(pubkey, 8, 5)
        assert converted is not None
        encoded = bech32.bech32_encode(HRP, converted)
        return encoded

    def is_contract_address(self):
        return self.hex().startswith(SC_HEX_PUBKEY_PREFIX)

    def __repr__(self):
        return self.bech32()


def _decode_bech32(value: str):
    hrp, value_bytes = bech32.bech32_decode(value)
    if hrp != HRP or value_bytes is None:
        raise ErrBadAddress(value)

    decoded_bytes = bech32.convertbits(value_bytes, 5, 8, False)
    if decoded_bytes is None:
        raise ErrBadAddress(value)

    return bytearray(decoded_bytes)
