import re

import pytest

from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.core.code_metadata import CodeMetadata


def test_new_from_code_metadata():
    value = CodeMetadataValue.new_from_code_metadata(CodeMetadata())
    assert value.get_payload() == bytes([0x05, 0x00])

    value = CodeMetadataValue.new_from_code_metadata(CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True))
    assert value.get_payload() == bytes([0x05, 0x06])


def test_set_payload_and_get_payload():
    # Simple
    value = CodeMetadataValue()
    value.set_payload(bytes([0x05, 0x00]))
    assert value.get_payload() == bytes([0x05, 0x00])

    # With CodeMetadata
    value = CodeMetadataValue()
    value.set_payload(CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True))
    assert value.get_payload() == bytes([0x05, 0x06])

    # From dictionary
    value = CodeMetadataValue()
    value.set_payload({
        "hex": "0500"
    })
    assert value.get_payload() == bytes([0x05, 0x00])

    # With errors
    with pytest.raises(ValueError, match=re.escape("cannot set payload for code metadata (should be either a CodeMetadata, bytes or dict, but got: <class 'int'>)")):
        CodeMetadataValue().set_payload(5)

    with pytest.raises(ValueError, match="code metadata buffer has length 4, expected 2"):
        CodeMetadataValue().set_payload(bytes([0, 1, 2, 3]))
