from types import SimpleNamespace

import pytest

from multiversx_sdk.abi.shared import (convert_native_value_to_dictionary,
                                       convert_native_value_to_list)


def test_convert_native_value_to_dictionary():
    # Simple namespace
    dictionary, ok = convert_native_value_to_dictionary(SimpleNamespace(a=1, b=2, c=3))
    assert dictionary == {"a": 1, "b": 2, "c": 3}
    assert ok

    # Dictionary
    dictionary, ok = convert_native_value_to_dictionary({"a": 1, "b": 2, "c": 3})
    assert dictionary == {"a": 1, "b": 2, "c": 3}
    assert ok

    # With errors
    dictionary, ok = convert_native_value_to_dictionary(42, raise_on_failure=False)
    assert dictionary == {}
    assert not ok

    # With errors (raise on failure)
    with pytest.raises(ValueError, match="cannot convert native value to dictionary"):
        dictionary, ok = convert_native_value_to_dictionary(42)

    with pytest.raises(ValueError, match="cannot convert native value to dictionary"):
        dictionary, ok = convert_native_value_to_dictionary([42, 43])


def test_convert_native_value_to_list():
    # List
    items, ok = convert_native_value_to_list([1, 2, 3])
    assert items == [1, 2, 3]
    assert ok

    # With errors
    items, ok = convert_native_value_to_list(42, raise_on_failure=False)
    assert items == []
    assert not ok

    # With errors (raise on failure)
    with pytest.raises(ValueError, match="cannot properly convert dictionary to list"):
        items, ok = convert_native_value_to_list(
            {
                "a": 1,
                "b": 2,
                "c": 3
            }
        )

    with pytest.raises(ValueError, match="cannot convert native value to list"):
        items, ok = convert_native_value_to_list(42)

    with pytest.raises(ValueError, match="cannot convert native value to list"):
        items, ok = convert_native_value_to_list(SimpleNamespace(a=1, b=2, c=3))
