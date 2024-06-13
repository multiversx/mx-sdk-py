from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.option_value import OptionValue
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.struct_value import StructValue


def test_set_payload_and_get_payload():
    # Simple (provided)
    value = OptionValue(U32Value())
    value.set_payload(42)
    assert value.get_payload() == 42

    # Simple (missing)
    value = OptionValue(U32Value())
    value.set_payload(None)
    assert value.get_payload() is None

    # Nested
    value = OptionValue(StructValue([
        Field("a", U32Value()),
        Field("b", BigUIntValue())
    ]))

    value.set_payload({"a": 41, "b": 42})
    assert value.get_payload() == SimpleNamespace(a=41, b=42)

    # With errors
    with pytest.raises(ValueError, match="placeholder value of option should be set before calling set_payload"):
        OptionValue().set_payload(42)
