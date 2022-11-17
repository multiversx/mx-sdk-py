
import pytest

from erdpy_core.address import Address
from erdpy_core.errors import ErrBadAddress, ErrBadPubkeyLength


def test_address():
    address = Address.from_bech32("erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz")
    assert "fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293" == address.hex()
    assert "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz" == address.bech32()

    address = Address(bytes.fromhex("fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293"))
    assert "fd691bb5e85d102687d81079dffce842d4dc328276d2d4c60d8fd1c3433c3293" == address.hex()
    assert "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz" == address.bech32()

    with pytest.raises(ErrBadPubkeyLength):
        address = Address(bytes())

    with pytest.raises(ErrBadAddress):
        address = Address.from_bech32("bad")
