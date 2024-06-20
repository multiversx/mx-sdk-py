from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.array_value import ArrayValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.codec import Codec
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.small_int_values import U16Value, U32Value
from multiversx_sdk.abi.struct_value import StructValue


def test_set_payload_and_get_payload():
    # Simple
    value = ArrayValue(length=3, item_creator=lambda: U32Value())
    value.set_payload([1, 2, 3])
    assert value.items == [U32Value(1), U32Value(2), U32Value(3)]
    assert value.get_payload() == [1, 2, 3]

    # Simple
    value = ArrayValue(length=3, items=[BigUIntValue(4), BigUIntValue(5), BigUIntValue(6)], item_creator=lambda: BigUIntValue())
    assert value.items == [BigUIntValue(4), BigUIntValue(5), BigUIntValue(6)]
    assert value.get_payload() == [4, 5, 6]

    value.set_payload(range(7, 10))
    assert value.items == [BigUIntValue(7), BigUIntValue(8), BigUIntValue(9)]
    assert value.get_payload() == [7, 8, 9]

    # Simple
    value = ArrayValue(length=3, item_creator=lambda: BigUIntValue())
    value.set_payload(range(4, 7))
    assert value.items == [BigUIntValue(4), BigUIntValue(5), BigUIntValue(6)]
    assert value.get_payload() == [4, 5, 6]

    # Nested (with recursion)
    value = ArrayValue(length=3, item_creator=lambda: StructValue([
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
    with pytest.raises(ValueError, match="populating an array from a native object requires the item creator to be set"):
        value = ArrayValue(length=3)
        value.set_payload([1, 2, 3])

    # With errors
    with pytest.raises(ValueError, match="wrong length, expected: 2, actual: 3"):
        value = ArrayValue(length=2, item_creator=lambda: U32Value())
        value.set_payload([1, 2, 3])

    # With errors
    with pytest.raises(ValueError, match="cannot convert native value to list, because of: 'int' object is not iterable"):
        value = ArrayValue(length=1, item_creator=lambda: U32Value())
        value.set_payload(42)


def test_encode_top_level():
    codec = Codec()
    array_value = ArrayValue(length=3, items=[U16Value(1), U16Value(2), U16Value(3)])

    encoded = codec.encode_top_level(array_value)
    assert encoded.hex() == "000100020003"


def test_encode_nested():
    codec = Codec()
    array_value = ArrayValue(length=3, items=[U16Value(1), U16Value(2), U16Value(3)])

    encoded = codec.encode_nested(array_value)
    assert encoded.hex() == "000100020003"


def test_decode_top_level():
    codec = Codec()
    data = bytes.fromhex("000100020003")

    destination = ArrayValue(length=3, item_creator=lambda: U16Value())
    codec.decode_top_level(data, destination)

    assert destination.items == [U16Value(1), U16Value(2), U16Value(3)]


def test_decode_nested():
    codec = Codec()
    data = bytes.fromhex("000100020003")

    destination = ArrayValue(length=3, item_creator=lambda: U16Value())
    codec.decode_nested(data, destination)

    assert destination.items == [U16Value(1), U16Value(2), U16Value(3)]
