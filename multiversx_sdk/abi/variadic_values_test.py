import re

import pytest

from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.variadic_values import VariadicValues


def test_set_payload_and_get_payload():
    # Simple
    values = VariadicValues(item_creator=lambda: U32Value())
    values.set_payload([1, 2, 3])

    assert values.items == [U32Value(1), U32Value(2), U32Value(3)]
    assert values.get_payload() == [1, 2, 3]

    # Nested
    values = VariadicValues(item_creator=lambda: MultiValue([U32Value(), StringValue()]))
    values.set_payload([[42, "hello"], [43, "world"]])

    assert values.items == [
        MultiValue([U32Value(42), StringValue("hello")]),
        MultiValue([U32Value(43), StringValue("world")])
    ]

    assert values.get_payload() == [[42, "hello"], [43, "world"]]

    # With errors
    with pytest.raises(ValueError, match="populating variadic values from a native object requires the item creator to be set"):
        VariadicValues().set_payload([1, 2, 3])

    # With errors
    with pytest.raises(ValueError, match=re.escape("invalid literal for int() with base 10: 'foo'")):
        values = VariadicValues(item_creator=lambda: U32Value())
        values.set_payload(["foo"])
