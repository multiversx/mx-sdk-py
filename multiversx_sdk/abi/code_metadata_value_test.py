import re

import pytest

from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.core.code_metadata import CodeMetadata


def test_set_payload_and_get_payload():
    # Simple
    value = CodeMetadataValue()
    value.set_payload(bytes([0x05, 0x00]))
    assert value.get_payload() == bytes([0x05, 0x00])

    # From CodeMetadata
    value = CodeMetadataValue()
    value.set_payload(CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True))
    assert value.get_payload() == bytes([0x05, 0x06])

    # With errors
    with pytest.raises(ValueError, match=re.escape("cannot set payload for code metadata (should be either a CodeMetadata or bytes, but got: <class 'dict'>)")):
        CodeMetadataValue().set_payload({})

    with pytest.raises(ValueError, match="code metadata buffer has length 4, expected 2"):
        CodeMetadataValue().set_payload(bytes([0, 1, 2, 3]))
