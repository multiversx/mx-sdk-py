from typing import Tuple

from Cryptodome.Hash import keccak

from erdpy_core import bech32
from erdpy_core.constants import METACHAIN_ID
from erdpy_core.errors import ErrBadAddress, ErrBadPubkeyLength
from erdpy_core.interfaces import IAddress, INonce

SC_HEX_PUBKEY_PREFIX = "0" * 16
DEFAULT_HRP = "erd"
PUBKEY_LENGTH = 32
PUBKEY_STRING_LENGTH = PUBKEY_LENGTH * 2  # hex-encoded
BECH32_LENGTH = 62


class Address():
    def __init__(self, pubkey: bytes, hrp: str):
        if len(pubkey) != PUBKEY_LENGTH:
            raise ErrBadPubkeyLength(len(pubkey), PUBKEY_LENGTH)

        self.pubkey = bytes(pubkey)
        self.hrp = hrp

    @classmethod
    def from_bech32(cls, value: str) -> 'Address':
        hrp, pubkey = _decode_bech32(value)
        return cls(pubkey, hrp)

    @classmethod
    def from_hex(cls, value: str, hrp: str) -> 'Address':
        pubkey = bytes.fromhex(value)
        return cls(pubkey, hrp)

    def hex(self) -> str:
        return self.pubkey.hex()

    def bech32(self) -> str:
        converted = bech32.convertbits(self.pubkey, 8, 5)
        assert converted is not None
        encoded = bech32.bech32_encode(self.hrp, converted)
        return encoded

    def is_smart_contract(self):
        return self.hex().startswith(SC_HEX_PUBKEY_PREFIX)

    def get_shard(self) -> int:
        shard = get_shard_of_pubkey(self.pubkey)
        return shard

    def serialize(self) -> bytes:
        return self.pubkey

    def __repr__(self):
        return self.bech32()


class AddressFactory():
    def __init__(self, hrp: str = DEFAULT_HRP) -> None:
        self.hrp = hrp

    def create_zero(self) -> Address:
        return Address(bytearray(32), self.hrp)

    def create_from_bech32(self, value: str) -> Address:
        hrp, pubkey = _decode_bech32(value)
        if hrp != self.hrp:
            raise ErrBadAddress(value)

        return Address(pubkey, hrp)

    def create_from_pubkey(self, pubkey: bytes) -> Address:
        return Address(pubkey, self.hrp)

    def create_from_hex(self, value: str) -> Address:
        return Address.from_hex(value, self.hrp)


class AddressConverter():
    def __init__(self, hrp: str = DEFAULT_HRP) -> None:
        self.hrp = hrp

    def bech32_to_pubkey(self, value: str) -> bytes:
        hrp, pubkey = _decode_bech32(value)
        if hrp != self.hrp:
            raise ErrBadAddress(value)

        return pubkey

    def pubkey_to_bech32(self, pubkey: bytes) -> str:
        address = Address(pubkey, self.hrp)
        return address.bech32()


def is_valid_bech32(value: str, expected_hrp: str) -> bool:
    hrp, value_bytes = bech32.bech32_decode(value)
    return hrp == expected_hrp and value_bytes is not None


def _decode_bech32(value: str) -> Tuple[str, bytes]:
    hrp, value_bytes = bech32.bech32_decode(value)
    if hrp is None or value_bytes is None:
        raise ErrBadAddress(value)

    decoded_bytes = bech32.convertbits(value_bytes, 5, 8, False)
    if decoded_bytes is None:
        raise ErrBadAddress(value)

    return hrp, bytearray(decoded_bytes)


def get_shard_of_pubkey(pubkey: bytes) -> int:
    num_shards = 3
    mask_high = int("11", 2)
    mask_low = int("01", 2)

    last_byte_of_pubkey = pubkey[31]

    if _is_pubkey_of_metachain(pubkey):
        return METACHAIN_ID

    shard = last_byte_of_pubkey & mask_high
    if shard > num_shards - 1:
        shard = last_byte_of_pubkey & mask_low

    return shard


def _is_pubkey_of_metachain(pubkey: bytes) -> bool:
    metachain_prefix = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    pubkey_prefix = pubkey[0:len(metachain_prefix)]
    if pubkey_prefix == metachain_prefix:
        return True

    zero_address = bytearray(32)
    if pubkey == zero_address:
        return True

    return False


def compute_contract_address(deployer: IAddress, deployment_nonce: INonce, address_hrp: str) -> Address:
    """
    8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
    """
    _, deployer_pubkey = _decode_bech32(deployer.bech32())
    nonce_bytes = deployment_nonce.to_bytes(8, byteorder="little")
    bytes_to_hash = deployer_pubkey + nonce_bytes
    contract_pubkey = keccak.new(digest_bits=256).update(bytes_to_hash).digest()
    contract_pubkey = bytes([0] * 8) + bytes([5, 0]) + contract_pubkey[10:30] + deployer_pubkey[30:]
    return Address(contract_pubkey, address_hrp)
