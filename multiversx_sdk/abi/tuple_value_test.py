import re

import pytest

from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.tuple_value import TupleValue


def test_set_payload_and_get_payload():
    # With errors
    with pytest.raises(ValueError, match=re.escape("cannot set payload for tuple (should be either a tuple or a list)")):
        TupleValue([]).set_payload(42)

    value = TupleValue([
        U32Value(),
        StringValue(),
    ])

    # From tuple
    value.set_payload((41, "hello"))
    assert value.fields == [U32Value(41), StringValue("hello")]
    assert value.get_payload() == (41, "hello")

    # From list
    value.set_payload([42, "world"])
    assert value.fields == [U32Value(42), StringValue("world")]
    assert value.get_payload() == (42, "world")
