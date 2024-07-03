import re
from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.struct_value import StructValue


def test_set_payload_and_get_payload():
    # With errors
    with pytest.raises(ValueError, match=re.escape("cannot set payload for struct (should be either a dictionary or a list)")):
        StructValue([]).set_payload(42)

    value = StructValue([
        Field("a", U32Value()),
        Field("b", BigUIntValue())
    ])

    # From list
    value.set_payload([39, 40])
    assert value.fields == [Field("a", U32Value(39)), Field("b", BigUIntValue(40))]
    assert value.get_payload() == SimpleNamespace(a=39, b=40)

    # From SimpleNamespace
    value.set_payload(SimpleNamespace(a=41, b=42))
    assert value.fields == [Field("a", U32Value(41)), Field("b", BigUIntValue(42))]
    assert value.get_payload() == SimpleNamespace(a=41, b=42)

    class Payload:
        def __init__(self, a: int, b: int):
            self.a = a
            self.b = b

    # Then, from object
    value.set_payload(Payload(43, 44))
    assert value.fields == [Field("a", U32Value(43)), Field("b", BigUIntValue(44))]
    assert value.get_payload() == SimpleNamespace(a=43, b=44)

    # Then, from dictionary
    value.set_payload({"a": 45, "b": 46})
    assert value.fields == [Field("a", U32Value(45)), Field("b", BigUIntValue(46))]
    assert value.get_payload() == SimpleNamespace(a=45, b=46)
