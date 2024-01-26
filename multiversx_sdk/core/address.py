import logging
from typing import Protocol, Tuple

from Cryptodome.Hash import keccak

from multiversx_sdk_core import bech32
from multiversx_sdk_core.constants import DEFAULT_HRP, METACHAIN_ID
from multiversx_sdk_core.errors import ErrBadAddress, ErrBadPubkeyLength

SC_HEX_PUBKEY_PREFIX = "0" * 16
PUBKEY_LENGTH = 32
PUBKEY_STRING_LENGTH = PUBKEY_LENGTH * 2  # hex-encoded
BECH32_LENGTH = 62

logger = logging.getLogger("address")


class IAddress(Protocol):
    def get_public_key(self) -> bytes:
        ...

    def get_hrp(self) -> str:
        ...


class Address:
    def __init__(self, pubkey: bytes, hrp: str) -> None:
        if len(pubkey) != PUBKEY_LENGTH:
            raise ErrBadPubkeyLength(len(pubkey), PUBKEY_LENGTH)

        self.pubkey = bytes(pubkey)
        self.hrp = hrp

    @classmethod
    def new_from_bech32(cls, value: str) -> 'Address':
        hrp, pubkey = _decode_bech32(value)
        return cls(pubkey, hrp)

    @classmethod
    def from_bech32(cls, value: str) -> 'Address':
        """The `from_bech32()` method is deprecated. Please use `new_from_bech32()` instead"""
        return Address.new_from_bech32(value)

    @classmethod
    def new_from_hex(cls, value: str, hrp: str) -> 'Address':
        pubkey = bytes.fromhex(value)
        return cls(pubkey, hrp)

    @classmethod
    def from_hex(cls, value: str, hrp: str) -> 'Address':
        """The `from_hex()` method is deprecated. Please use `new_from_hex()` instead"""
        return Address.new_from_hex(value, hrp)

    def to_hex(self) -> str:
        return self.pubkey.hex()

    def hex(self) -> str:
        """The `hex()` method is deprecated. Please use `to_hex()` instead"""
        return self.to_hex()

    def to_bech32(self) -> str:
        converted = bech32.convertbits(self.pubkey, 8, 5)
        assert converted is not None
        encoded = bech32.bech32_encode(self.hrp, converted)
        return encoded

    def bech32(self) -> str:
        """The `bech32()` method is deprecated. Please us `to_bech32()` instead"""
        return self.to_bech32()

    def get_public_key(self) -> bytes:
        return self.pubkey

    def get_hrp(self) -> str:
        return self.hrp

    def is_smart_contract(self):
        return self.to_hex().startswith(SC_HEX_PUBKEY_PREFIX)

    # this will be removed in v1.0.0; it's here for compatibility reasons with the deprecated transaction builders
    # the transaction builders will also be removed in v1.0.0
    def serialize(self) -> bytes:
        logger.warning("The `serialize()` method is deprecated and will soon be removed")
        return self.get_public_key()


class AddressFactory:
    def __init__(self, hrp: str = DEFAULT_HRP) -> None:
        self.hrp = hrp

    def create_from_bech32(self, value: str) -> Address:
        hrp, pubkey = _decode_bech32(value)
        if hrp != self.hrp:
            raise ErrBadAddress(value)

        return Address(pubkey, hrp)

    def create_from_public_key(self, pubkey: bytes) -> Address:
        return Address(pubkey, self.hrp)

    def create_from_hex(self, value: str) -> Address:
        return Address.new_from_hex(value, self.hrp)


class AddressComputer:
    def __init__(self, number_of_shards: int = 3) -> None:
        self.number_of_shards = number_of_shards

    def compute_contract_address(self, deployer: IAddress, deployment_nonce: int) -> Address:
        """
        8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
        """
        deployer_pubkey = deployer.get_public_key()
        nonce_bytes = deployment_nonce.to_bytes(8, byteorder="little")
        bytes_to_hash = deployer_pubkey + nonce_bytes
        contract_pubkey = keccak.new(digest_bits=256).update(bytes_to_hash).digest()
        contract_pubkey = bytes([0] * 8) + bytes([5, 0]) + contract_pubkey[10:30] + deployer_pubkey[30:]
        return Address(contract_pubkey, deployer.get_hrp())

    def get_shard_of_address(self, address: IAddress) -> int:
        return get_shard_of_pubkey(address.get_public_key(), self.number_of_shards)


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

    return hrp, bytes(bytearray(decoded_bytes))


def get_shard_of_pubkey(pubkey: bytes, number_of_shards: int) -> int:
    mask_high = int("11", 2)
    mask_low = int("01", 2)

    last_byte_of_pubkey = pubkey[31]

    if _is_pubkey_of_metachain(pubkey):
        return METACHAIN_ID

    shard = last_byte_of_pubkey & mask_high
    if shard > number_of_shards - 1:
        shard = last_byte_of_pubkey & mask_low

    return shard


def _is_pubkey_of_metachain(pubkey: bytes) -> bool:
    metachain_prefix = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    pubkey_prefix = pubkey[0:len(metachain_prefix)]
    if pubkey_prefix == bytes(metachain_prefix):
        return True

    zero_address = bytearray(32)
    if pubkey == bytes(zero_address):
        return True

    return False
