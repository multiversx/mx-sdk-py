import re
from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.core.address import Address


def test_set_payload_and_get_payload():
    # Simple
    pubkey = bytes.fromhex("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1")
    value = AddressValue()
    value.set_payload(pubkey)
    assert value.get_payload() == pubkey

    # Simple (from Address)
    address = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    value = AddressValue()
    value.set_payload(address)
    assert value.get_payload() == address.get_public_key()

    # From dict using a bech32 address
    address = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    value = AddressValue()
    value.set_payload(
        {
            "bech32": address.to_bech32()
        }
    )
    assert value.get_payload() == address.get_public_key()

    # From dict using a hex address
    address = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    value = AddressValue()
    value.set_payload(
        {
            "hex": address.to_hex()
        }
    )
    assert value.get_payload() == address.get_public_key()

    # With errors
    with pytest.raises(ValueError, match=re.escape("public key (address) has invalid length: 3")):
        AddressValue().set_payload(bytes([1, 2, 3]))

    # With errors
    with pytest.raises(TypeError, match="cannot convert 'types.SimpleNamespace' object to bytes"):
        AddressValue().set_payload(SimpleNamespace(a=1, b=2, c=3))

    # With errors
    with pytest.raises(ValueError, match="cannot extract pubkey from dictionary: missing 'bech32' or 'hex' keys"):
        AddressValue().set_payload({})
