
import pytest

from erdpy_core.address import Address, AddressConverter, AddressFactory
from erdpy_core.errors import ErrBadAddress, ErrBadPubkeyLength


def test_address():
    address = Address.from_bech32("erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz")
    assert "fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293" == address.hex()
    assert "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz" == address.bech32()

    address = Address.from_hex("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293", "erd")
    assert "fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293" == address.hex()
    assert "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz" == address.bech32()

    with pytest.raises(ErrBadPubkeyLength):
        address = Address(bytes(), "erd")

    with pytest.raises(ErrBadAddress):
        address = Address.from_bech32("bad")


def test_address_with_custom_hrp():
    address = Address.from_hex("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1", "test")
    assert address.hrp == "test"
    assert address.bech32() == "test1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ss5hqhtr"

    address = Address.from_bech32("test1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ss5hqhtr")
    assert address.hrp == "test"
    assert address.hex() == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"


def test_address_converter():
    converter = AddressConverter("erd")
    pubkey = bytes.fromhex("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1")
    bech32 = "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"

    assert converter.bech32_to_pubkey(bech32) == pubkey
    assert converter.pubkey_to_bech32(pubkey) == bech32


def test_address_factory():
    factory_foo = AddressFactory("foo")
    factory_erd = AddressFactory("erd")
    pubkey = bytes.fromhex("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1")

    assert factory_foo.create_from_pubkey(pubkey).bech32() == "foo1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssunhpj4"
    assert factory_erd.create_from_pubkey(pubkey).bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
