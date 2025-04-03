import logging
from typing import Optional

from Cryptodome.Hash import keccak

from multiversx_sdk.core import bech32
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.constants import METACHAIN_ID
from multiversx_sdk.core.errors import BadAddressError, BadPubkeyLengthError

SC_HEX_PUBKEY_PREFIX = "0" * 16
PUBKEY_LENGTH = 32

logger = logging.getLogger("address")


class Address:
    """An Address, as an immutable object."""

    def __init__(self, pubkey: bytes, hrp: Optional[str] = None) -> None:
        """Creates an address object, given a sequence of bytes and the human readable part(hrp).

        Args:
            pubkey (bytes): the sequence of bytes\n
            hrp (str): the human readable part"""

        # used for creating an empty address
        if not len(pubkey):
            self.pubkey = bytes()
            self.hrp = LibraryConfig.default_address_hrp
            return

        if len(pubkey) != PUBKEY_LENGTH:
            raise BadPubkeyLengthError(len(pubkey), PUBKEY_LENGTH)

        self.pubkey = bytes(pubkey)
        self.hrp = hrp if hrp else LibraryConfig.default_address_hrp

    @classmethod
    def empty(cls) -> "Address":
        """
        Creates an empty address object.
        Generally speaking, this should not be used by client code **(internal use only)**.
        """
        return cls(b"", "")

    def is_empty(self) -> bool:
        return len(self.pubkey) == 0

    @classmethod
    def new_from_bech32(cls, value: str) -> "Address":
        """Creates an address object from the bech32 representation of an address.

        Args:
            value (str): the bech32 address representation"""
        hrp, pubkey = _decode_bech32(value)
        return cls(pubkey, hrp)

    @classmethod
    def from_bech32(cls, value: str) -> "Address":
        """The `from_bech32()` method is deprecated. Please use `new_from_bech32()` instead"""
        return cls.new_from_bech32(value)

    @classmethod
    def new_from_hex(cls, value: str, hrp: Optional[str] = None) -> "Address":
        """Creates an address object from the hexed sequence of bytes and the human readable part(hrp).

        Args:
            value (str): the sequence of bytes as a hex string\n
            hrp (str): the human readable part"""
        pubkey = bytes.fromhex(value)
        return cls(pubkey, hrp)

    @classmethod
    def from_hex(cls, value: str, hrp: str) -> "Address":
        """The `from_hex()` method is deprecated. Please use `new_from_hex()` instead"""
        return cls.new_from_hex(value, hrp)

    def to_hex(self) -> str:
        """Returns the hex representation of the address (pubkey)"""
        return self.pubkey.hex()

    def hex(self) -> str:
        """The `hex()` method is deprecated. Please use `to_hex()` instead"""
        return self.to_hex()

    def to_bech32(self) -> str:
        """Returns the bech32 representation of the address"""
        if self.is_empty():
            return ""

        converted = bech32.convertbits(self.pubkey, 8, 5)
        assert converted is not None
        encoded = bech32.bech32_encode(self.hrp, converted)
        return encoded

    def bech32(self) -> str:
        """The `bech32()` method is deprecated. Please us `to_bech32()` instead"""
        return self.to_bech32()

    def get_public_key(self) -> bytes:
        """Returns the pubkey as bytes"""
        return self.pubkey

    def get_hrp(self) -> str:
        """Returns the human-readable-part of the bech32 address"""
        return self.hrp

    def is_smart_contract(self) -> bool:
        """Returns whether the address is a smart contract address"""
        return self.to_hex().startswith(SC_HEX_PUBKEY_PREFIX)

    def __bytes__(self) -> bytes:
        return self.get_public_key()

    def __str__(self) -> str:
        return self.to_bech32()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return False

        return self.pubkey == other.pubkey and self.hrp == other.hrp


class AddressFactory:
    """A factory used to create address objects."""

    def __init__(self, hrp: Optional[str] = None) -> None:
        """All the addresses created with the factory have the same human readable part

        Args:
            hrp (str): the human readable part of the address (default: erd)"""
        self.hrp = hrp if hrp else LibraryConfig.default_address_hrp

    def create_from_bech32(self, value: str) -> Address:
        """Creates an address object from the bech32 representation of an address"""
        hrp, pubkey = _decode_bech32(value)
        if hrp != self.hrp:
            raise BadAddressError(value)

        return Address(pubkey, hrp)

    def create_from_public_key(self, pubkey: bytes) -> Address:
        """Creates an address object from the sequence of bytes"""
        return Address(pubkey, self.hrp)

    def create_from_hex(self, value: str) -> Address:
        """Creates an address object from the hexed sequence of bytes"""
        return Address.new_from_hex(value, self.hrp)


class AddressComputer:
    """A class for computing contract addresses and getting shard numbers."""

    def __init__(self, number_of_shards: int = 3) -> None:
        """Initializes the AddressComputer with the number of shards.

        Args:
            number_of_shards (int): The number of shards in the network (default: 3)."""
        self.number_of_shards = number_of_shards

    def compute_contract_address(self, deployer: Address, deployment_nonce: int) -> Address:
        """Computes the contract address based on the deployer's address and deployment nonce.

        Args:
            deployer (Address): The address of the deployer\n
            deployment_nonce (int): The nonce of the deployment

        Returns:
            Address: The computed contract address as below:

            8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
        """
        deployer_pubkey = deployer.get_public_key()
        nonce_bytes = deployment_nonce.to_bytes(8, byteorder="little")
        bytes_to_hash = deployer_pubkey + nonce_bytes
        contract_pubkey = keccak.new(digest_bits=256).update(bytes_to_hash).digest()
        contract_pubkey = bytes([0] * 8) + bytes([5, 0]) + contract_pubkey[10:30] + deployer_pubkey[30:]
        return Address(contract_pubkey, deployer.get_hrp())

    def get_shard_of_address(self, address: Address) -> int:
        """Returns the shard number of a given address.

        Args:
            address (Address): The address for which to determine the shard.

        Returns:
            int: The shard number."""
        return get_shard_of_pubkey(address.get_public_key(), self.number_of_shards)


def is_valid_bech32(value: str, expected_hrp: str) -> bool:
    hrp, value_bytes = bech32.bech32_decode(value)
    return hrp == expected_hrp and value_bytes is not None


def _decode_bech32(value: str) -> tuple[str, bytes]:
    hrp, value_bytes = bech32.bech32_decode(value)
    if hrp is None or value_bytes is None:
        raise BadAddressError(value)

    decoded_bytes = bech32.convertbits(value_bytes, 5, 8, False)
    if decoded_bytes is None:
        raise BadAddressError(value)

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
    pubkey_prefix = pubkey[0 : len(metachain_prefix)]
    if pubkey_prefix == bytes(metachain_prefix):
        return True

    zero_address = bytearray(32)
    if pubkey == bytes(zero_address):
        return True

    return False
