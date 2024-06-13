import pytest

from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.string_value import StringValue


def test_set_payload_and_get_payload():
    # Simple
    value = MultiValue([
        U32Value(),
        StringValue(),
    ])

    value.set_payload([1, "hello"])

    assert value.items == [U32Value(1), StringValue("hello")]
    assert value.get_payload() == [1, "hello"]

    # Nested
    value = MultiValue([
        StringValue(),
        StringValue(),
        MultiValue([
            U32Value(),
            StringValue(),
        ])
    ])

    value.set_payload(["a", "b", [42, "hello"]])

    assert value.items == [
        StringValue("a"),
        StringValue("b"),
        MultiValue([U32Value(42), StringValue("hello")])
    ]

    assert value.get_payload() == ["a", "b", [42, "hello"]]

    # With errors
    with pytest.raises(ValueError, match="cannot convert native value to list, because of: 'int' object is not iterable"):
        value = MultiValue([U32Value(), StringValue()])
        value.set_payload(42)

    # With errors
    with pytest.raises(ValueError, match="for multi-value, expected 2 items, got 3"):
        value = MultiValue([U32Value(), StringValue()])
        value.set_payload([42, "hello", "world"])
