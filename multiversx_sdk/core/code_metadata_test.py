

import pytest

from multiversx_sdk.core.code_metadata import CodeMetadata


def test_code_metadata_new_from_bytes():
    metadata = CodeMetadata.new_from_bytes(bytes([0x05, 0x00]))
    assert metadata.upgradeable == True
    assert metadata.readable == True
    assert metadata.payable == False
    assert metadata.payable_by_contract == False

    metadata = CodeMetadata.new_from_bytes(bytes([0x05, 0x06]))
    assert metadata.upgradeable == True
    assert metadata.readable == True
    assert metadata.payable == True
    assert metadata.payable_by_contract == True

    metadata = CodeMetadata.new_from_bytes(bytes([0x05, 0x04]))
    assert metadata.upgradeable == True
    assert metadata.readable == True
    assert metadata.payable == False
    assert metadata.payable_by_contract == True

    metadata = CodeMetadata.new_from_bytes(bytes([0x00, 0x00]))
    assert metadata.upgradeable == False
    assert metadata.readable == False
    assert metadata.payable == False
    assert metadata.payable_by_contract == False

    with pytest.raises(ValueError, match="code metadata buffer has length 4, expected 2"):
        CodeMetadata.new_from_bytes(bytes([0x00, 0x01, 0x02, 0x03]))


def test_code_metadata_serialize():
    assert CodeMetadata().serialize() == bytes([0x05, 0x00])
    assert CodeMetadata(upgradeable=True, readable=True).serialize() == bytes([0x05, 0x00])
    assert CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True).serialize() == bytes([0x05, 0x06])
    assert CodeMetadata(upgradeable=True, readable=True, payable=False, payable_by_contract=True).serialize() == bytes([0x05, 0x04])
    assert CodeMetadata(upgradeable=False, readable=False, payable=False, payable_by_contract=False).serialize() == bytes([0x00, 0x00])
