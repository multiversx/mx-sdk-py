from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.small_int_values import U32Value, U64Value
from multiversx_sdk.abi.typesystem import (is_bytes, is_list_of_bytes,
                                           is_list_of_typed_values,
                                           is_multi_value, is_single_value,
                                           is_typed_value)
from multiversx_sdk.abi.variadic_values import VariadicValues


def test_is_list_of_bytes():
    assert is_list_of_bytes([b"a", b"b", b"c"])
    assert is_list_of_bytes([bytes([1, 2, 3]), bytes([4, 5, 6])])

    assert not is_list_of_bytes([b"a", b"b", "c"])
    assert not is_list_of_bytes([b"a", b"b", [1, 2, 3]])


def test_is_bytes():
    assert is_bytes(b"hello")
    assert is_bytes(bytes([1, 2, 3]))

    assert not is_bytes("hello")
    assert not is_bytes([1, 2, 3])


def test_is_list_of_typed_values():
    assert is_list_of_typed_values([U64Value(), U64Value()])
    assert is_list_of_typed_values([U32Value(), VariadicValues([U64Value(), U64Value()])])

    assert not is_list_of_typed_values([U64Value(), "hello"])
    assert not is_list_of_typed_values([U64Value(), [1, 2, 3]])


def test_is_typed_value():
    assert is_typed_value(U64Value())
    assert is_typed_value(ListValue([]))
    assert is_typed_value(MultiValue([]))
    assert is_typed_value(VariadicValues([]))
    assert is_typed_value(OptionalValue(U64Value()))

    assert not is_typed_value("hello")


def test_is_single_value():
    assert is_single_value(U64Value())
    assert is_single_value(ListValue([]))

    assert not is_single_value(MultiValue([]))
    assert not is_single_value(VariadicValues([]))
    assert not is_single_value("hello")


def test_is_multi_value():
    assert is_multi_value(MultiValue([]))
    assert is_multi_value(VariadicValues([]))

    assert not is_multi_value(U64Value())
    assert not is_multi_value(ListValue([]))
    assert not is_multi_value("hello")
