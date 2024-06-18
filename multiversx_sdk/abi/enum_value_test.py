import re
from types import SimpleNamespace
from typing import List

import pytest

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.enum_value import EnumValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.small_int_values import U32Value


def test_set_payload_and_get_payload():
    # With errors (missing fields provider)
    with pytest.raises(ValueError, match="populating an enum from a native object requires the fields provider to be set"):
        EnumValue().set_payload(42)

    # With errors (missing __discriminant__ field)
    with pytest.raises(ValueError, match=re.escape("for enums, the native object (when it's a dictionary) must contain the special field '__discriminant__'")):
        EnumValue(fields_provider=lambda discriminant: []).set_payload({})

    # Simple
    value = EnumValue(fields_provider=lambda discriminant: [])
    value.set_payload(42)
    assert value.discriminant == 42
    assert value.get_payload() == SimpleNamespace(__discriminant__=42)

    # With fields (from SimpleNamespace, object, dictionary or list)
    def provide_fields(discriminant: int) -> List[Field]:
        if discriminant == 41:
            return [
                Field("a", U32Value()),
                Field("b", BigUIntValue())
            ]

        if discriminant == 42:
            return [
                Field("c", U32Value()),
                Field("d", BigUIntValue())
            ]

        if discriminant == 43:
            return [
                Field("e", U32Value()),
                Field("f", BigUIntValue())
            ]

        if discriminant == 44:
            return [
                Field("g", U32Value()),
                Field("h", BigUIntValue())
            ]

        return []

    value = EnumValue(fields_provider=provide_fields)

    # First, from SimpleNamespace
    value.set_payload(SimpleNamespace(__discriminant__=41, a=1, b=2))
    assert value.discriminant == 41
    assert value.fields == [Field("a", U32Value(1)), Field("b", BigUIntValue(2))]
    assert value.get_payload() == SimpleNamespace(__discriminant__=41, a=1, b=2)

    class Payload:
        def __init__(self, c: int, d: int):
            self.__discriminant__ = 42
            self.c = c
            self.d = d

    # Then, from object
    value.set_payload(Payload(3, 4))
    assert value.discriminant == 42
    assert value.fields == [Field("c", U32Value(3)), Field("d", BigUIntValue(4))]
    assert value.get_payload() == SimpleNamespace(__discriminant__=42, c=3, d=4)

    # Then, from dictionary
    value.set_payload({"__discriminant__": 43, "e": 5, "f": 6})
    assert value.discriminant == 43
    assert value.fields == [Field("e", U32Value(5)), Field("f", BigUIntValue(6))]
    assert value.get_payload() == SimpleNamespace(__discriminant__=43, e=5, f=6)

    # Finally, from list (first element is the discriminant)
    value.set_payload([44, 7, 8])
    assert value.discriminant == 44
    assert value.fields == [Field("g", U32Value(7)), Field("h", BigUIntValue(8))]
    assert value.get_payload() == SimpleNamespace(__discriminant__=44, g=7, h=8)
