

from erdpy_core.code_metadata import CodeMetadata


def test_code_metadata_serialize():
    assert CodeMetadata().serialize() == bytes([0x05, 0x00])
    assert CodeMetadata(upgradeable=True, readable=True).serialize() == bytes([0x05, 0x00])
    assert CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True).serialize() == bytes([0x05, 0x06])
    assert CodeMetadata(upgradeable=True, readable=True, payable=False, payable_by_contract=True).serialize() == bytes([0x05, 0x04])
    assert CodeMetadata(upgradeable=False, readable=False, payable=False, payable_by_contract=False).serialize() == bytes([0x00, 0x00])
