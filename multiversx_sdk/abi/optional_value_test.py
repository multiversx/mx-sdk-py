import re

import pytest

from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.string_value import StringValue


def test_set_payload_and_get_payload():
    # Simple
    values = OptionalValue(U32Value())
    values.set_payload(42)

    assert values.value == U32Value(42)
    assert values.get_payload() == 42

    # Nested
    values = OptionalValue(MultiValue([U32Value(), StringValue()]))
    values.set_payload([42, "hello"])

    assert values.value == MultiValue([U32Value(42), StringValue("hello")])
    assert values.get_payload() == [42, "hello"]

    # With errors
    with pytest.raises(ValueError, match="placeholder value of optional should be set before calling set_payload"):
        OptionalValue().set_payload(42)
