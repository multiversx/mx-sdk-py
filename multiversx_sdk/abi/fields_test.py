import re

import pytest

from multiversx_sdk.abi.fields import (Field, set_fields_from_dictionary,
                                       set_fields_from_list)
from multiversx_sdk.abi.small_int_values import U32Value


def test_set_fields_from_dictionary():
    # Basic
    fields = [
        Field("a", U32Value()),
        Field("b", U32Value()),
        Field("c", U32Value())
    ]

    set_fields_from_dictionary(fields, {"a": 1, "b": 2, "c": 3})

    assert fields[0].value.get_payload() == 1
    assert fields[1].value.get_payload() == 2
    assert fields[2].value.get_payload() == 3

    # Missing field
    with pytest.raises(ValueError, match="the dictionary is missing the key 'c'"):
        set_fields_from_dictionary(fields, {"a": 1, "b": 2})

    # Bad type
    with pytest.raises(ValueError, match=re.escape("cannot set payload for field 'a', because of: invalid literal for int() with base 10: 'foobar'")):
        set_fields_from_dictionary(fields, {"a": "foobar", "b": 2, "c": 3})


def test_set_fields_from_list():
    # Basic
    fields = [
        Field("a", U32Value()),
        Field("b", U32Value()),
        Field("c", U32Value())
    ]

    set_fields_from_list(fields, [1, 2, 3])

    assert fields[0].value.get_payload() == 1
    assert fields[1].value.get_payload() == 2
    assert fields[2].value.get_payload() == 3

    # Missing field
    with pytest.raises(ValueError, match=re.escape("the number of fields (3) does not match the number of provided items (2)")):
        set_fields_from_list(fields, [1, 2])

    # Bad type
    with pytest.raises(ValueError, match=re.escape("cannot set payload for field 'a', because of: invalid literal for int() with base 10: 'foobar'")):
        set_fields_from_list(fields, ["foobar", 2, 3])
