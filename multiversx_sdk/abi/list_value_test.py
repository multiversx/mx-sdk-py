from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.struct_value import StructValue


def test_set_payload_and_get_payload():
    # Simple
    value = ListValue(item_creator=lambda: U32Value())
    value.set_payload([1, 2, 3])
    assert value.items == [U32Value(1), U32Value(2), U32Value(3)]
    assert value.get_payload() == [1, 2, 3]

    # Simple
    value = ListValue(item_creator=lambda: BigUIntValue())
    value.set_payload(range(4, 7))
    assert value.items == [BigUIntValue(4), BigUIntValue(5), BigUIntValue(6)]
    assert value.get_payload() == [4, 5, 6]

    # Nested (with recursion)
    value = ListValue(item_creator=lambda: StructValue([
        Field("a", U32Value()),
        Field("b", BigUIntValue())
    ]))

    value.set_payload([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6}
    ])

    assert value.items == [
        StructValue([Field("a", U32Value(1)), Field("b", BigUIntValue(2))]),
        StructValue([Field("a", U32Value(3)), Field("b", BigUIntValue(4))]),
        StructValue([Field("a", U32Value(5)), Field("b", BigUIntValue(6))])
    ]

    assert value.get_payload() == [
        SimpleNamespace(a=1, b=2),
        SimpleNamespace(a=3, b=4),
        SimpleNamespace(a=5, b=6)
    ]

    # With errors
    with pytest.raises(ValueError, match="populating a list from a native object requires the item creator to be set"):
        value = ListValue()
        value.set_payload([1, 2, 3])

    # With errors
    with pytest.raises(ValueError, match="cannot convert native value to list, because of: 'int' object is not iterable"):
        value = ListValue(item_creator=lambda: U32Value())
        value.set_payload(42)
