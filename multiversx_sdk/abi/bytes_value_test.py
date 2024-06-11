from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.bytes_value import BytesValue


def test_set_payload_and_get_payload():
    # Simple
    value = BytesValue()
    value.set_payload("hello")
    assert value.get_payload() == b"hello"

    # Simple
    value = BytesValue()
    value.set_payload(b"hello")
    assert value.get_payload() == b"hello"

    # With errors
    with pytest.raises(TypeError, match="cannot convert 'types.SimpleNamespace' object to bytes"):
        BytesValue().set_payload(SimpleNamespace(a=1, b=2, c=3))
