import re
from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.string_value import StringValue


def test_set_payload_and_get_payload():
    # Simple
    value = StringValue()
    value.set_payload("hello")
    assert value.get_payload() == "hello"

    # Simple
    value = StringValue()
    value.set_payload(b"hello")
    assert value.get_payload() == "hello"

    # With errors
    with pytest.raises(ValueError, match=re.escape("cannot set payload for string (should be either a string or bytes, but got: <class 'types.SimpleNamespace'>)")):
        StringValue().set_payload(SimpleNamespace(a=1, b=2, c=3))
