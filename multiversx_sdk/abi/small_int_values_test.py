import re
from typing import Protocol, Union

import pytest

from multiversx_sdk.abi.codec import Codec
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import (
    I8Value,
    I16Value,
    I32Value,
    I64Value,
    SmallIntValue,
    SmallUIntValue,
    U8Value,
    U16Value,
    U32Value,
    U64Value,
)

FixedWidthValue = Union[SmallUIntValue, SmallIntValue]


class FixedWidthValueType(Protocol):
    __name__: str

    def __call__(self, value: int = 0) -> FixedWidthValue: ...


FIXED_WIDTH_CASES = [
    pytest.param(U8Value, 0, 2**8 - 1, id="u8"),
    pytest.param(U16Value, 0, 2**16 - 1, id="u16"),
    pytest.param(U32Value, 0, 2**32 - 1, id="u32"),
    pytest.param(U64Value, 0, 2**64 - 1, id="u64"),
    pytest.param(I8Value, -(2**7), 2**7 - 1, id="i8"),
    pytest.param(I16Value, -(2**15), 2**15 - 1, id="i16"),
    pytest.param(I32Value, -(2**31), 2**31 - 1, id="i32"),
    pytest.param(I64Value, -(2**63), 2**63 - 1, id="i64"),
]

OUT_OF_RANGE_CASES = [
    pytest.param(U8Value, -1, 0, 2**8 - 1, id="u8-below-minimum"),
    pytest.param(U8Value, 2**8, 0, 2**8 - 1, id="u8-above-maximum"),
    pytest.param(U16Value, -1, 0, 2**16 - 1, id="u16-below-minimum"),
    pytest.param(U16Value, 2**16, 0, 2**16 - 1, id="u16-above-maximum"),
    pytest.param(U32Value, -1, 0, 2**32 - 1, id="u32-below-minimum"),
    pytest.param(U32Value, 2**32, 0, 2**32 - 1, id="u32-above-maximum"),
    pytest.param(U64Value, -1, 0, 2**64 - 1, id="u64-below-minimum"),
    pytest.param(U64Value, 2**64, 0, 2**64 - 1, id="u64-above-maximum"),
    pytest.param(I8Value, -(2**7) - 1, -(2**7), 2**7 - 1, id="i8-below-minimum"),
    pytest.param(I8Value, 2**7, -(2**7), 2**7 - 1, id="i8-above-maximum"),
    pytest.param(I16Value, -(2**15) - 1, -(2**15), 2**15 - 1, id="i16-below-minimum"),
    pytest.param(I16Value, 2**15, -(2**15), 2**15 - 1, id="i16-above-maximum"),
    pytest.param(I32Value, -(2**31) - 1, -(2**31), 2**31 - 1, id="i32-below-minimum"),
    pytest.param(I32Value, 2**31, -(2**31), 2**31 - 1, id="i32-above-maximum"),
    pytest.param(I64Value, -(2**63) - 1, -(2**63), 2**63 - 1, id="i64-below-minimum"),
    pytest.param(I64Value, 2**63, -(2**63), 2**63 - 1, id="i64-above-maximum"),
]


@pytest.mark.parametrize(("value_type", "minimum", "maximum"), FIXED_WIDTH_CASES)
def test_constructor_accepts_fixed_width_boundaries(
    value_type: FixedWidthValueType,
    minimum: int,
    maximum: int,
) -> None:
    assert value_type(minimum).get_payload() == minimum
    assert value_type(maximum).get_payload() == maximum


@pytest.mark.parametrize(
    ("value_type", "invalid_value", "minimum", "maximum"),
    OUT_OF_RANGE_CASES,
)
def test_constructor_rejects_values_outside_fixed_width_range(
    value_type: FixedWidthValueType,
    invalid_value: int,
    minimum: int,
    maximum: int,
) -> None:
    expected_message = (
        f"value {invalid_value} is out of range for {value_type.__name__}; " f"expected {minimum} <= value <= {maximum}"
    )

    with pytest.raises(ValueError, match=f"^{re.escape(expected_message)}$"):
        value_type(invalid_value)


@pytest.mark.parametrize(("value_type", "minimum", "maximum"), FIXED_WIDTH_CASES)
def test_set_payload_accepts_fixed_width_boundaries(
    value_type: FixedWidthValueType,
    minimum: int,
    maximum: int,
) -> None:
    value = value_type()

    value.set_payload(minimum)
    assert value.get_payload() == minimum

    value.set_payload(maximum)
    assert value.get_payload() == maximum


@pytest.mark.parametrize(
    ("value_type", "invalid_value", "minimum", "maximum"),
    OUT_OF_RANGE_CASES,
)
def test_set_payload_rejects_out_of_range_value_without_changing_payload(
    value_type: FixedWidthValueType,
    invalid_value: int,
    minimum: int,
    maximum: int,
) -> None:
    value = value_type(1)
    expected_message = (
        f"value {invalid_value} is out of range for {value_type.__name__}; " f"expected {minimum} <= value <= {maximum}"
    )

    with pytest.raises(ValueError, match=f"^{re.escape(expected_message)}$"):
        value.set_payload(invalid_value)

    assert value.get_payload() == 1


@pytest.mark.parametrize(
    ("target_type", "source_type", "target_num_bytes", "source_num_bytes"),
    [
        pytest.param(U8Value, U16Value, 1, 2, id="u8-from-u16"),
        pytest.param(U16Value, U32Value, 2, 4, id="u16-from-u32"),
        pytest.param(U32Value, U64Value, 4, 8, id="u32-from-u64"),
        pytest.param(I8Value, I16Value, 1, 2, id="i8-from-i16"),
        pytest.param(I16Value, I32Value, 2, 4, id="i16-from-i32"),
        pytest.param(I32Value, I64Value, 4, 8, id="i32-from-i64"),
    ],
)
def test_set_payload_rejects_wider_fixed_width_value(
    target_type: FixedWidthValueType,
    source_type: FixedWidthValueType,
    target_num_bytes: int,
    source_num_bytes: int,
) -> None:
    target = target_type()
    source = source_type(1)
    expected_message = (
        f"cannot set payload: source value has {source_num_bytes} bytes, "
        f"which is more than {target_num_bytes} bytes of the target"
    )

    with pytest.raises(ValueError, match=f"^{re.escape(expected_message)}$"):
        target.set_payload(source)

    assert target.get_payload() == 0


@pytest.mark.parametrize(
    ("target_type", "source", "expected_payload"),
    [
        pytest.param(U16Value, U8Value(2**8 - 1), 2**8 - 1, id="u16-from-u8"),
        pytest.param(U32Value, U16Value(2**16 - 1), 2**16 - 1, id="u32-from-u16"),
        pytest.param(U64Value, U32Value(2**32 - 1), 2**32 - 1, id="u64-from-u32"),
        pytest.param(I16Value, I8Value(-(2**7)), -(2**7), id="i16-from-i8"),
        pytest.param(I32Value, I16Value(-(2**15)), -(2**15), id="i32-from-i16"),
        pytest.param(I64Value, I32Value(-(2**31)), -(2**31), id="i64-from-i32"),
    ],
)
def test_set_payload_accepts_narrower_fixed_width_value(
    target_type: FixedWidthValueType,
    source: FixedWidthValue,
    expected_payload: int,
) -> None:
    target = target_type()

    target.set_payload(source)

    assert target.get_payload() == expected_payload


@pytest.mark.parametrize(
    ("value", "expected_top_level", "expected_nested"),
    [
        pytest.param(U8Value(0), "", "00", id="u8-minimum"),
        pytest.param(U8Value(2**8 - 1), "ff", "ff", id="u8-maximum"),
        pytest.param(U32Value(0), "", "00000000", id="u32-minimum"),
        pytest.param(U32Value(2**32 - 1), "ffffffff", "ffffffff", id="u32-maximum"),
        pytest.param(I8Value(-(2**7)), "80", "80", id="i8-minimum"),
        pytest.param(I8Value(2**7 - 1), "7f", "7f", id="i8-maximum"),
        pytest.param(I32Value(-(2**31)), "80000000", "80000000", id="i32-minimum"),
        pytest.param(I32Value(2**31 - 1), "7fffffff", "7fffffff", id="i32-maximum"),
    ],
)
def test_fixed_width_boundaries_preserve_top_level_and_nested_encoding(
    value: FixedWidthValue,
    expected_top_level: str,
    expected_nested: str,
) -> None:
    codec = Codec()

    assert codec.encode_top_level(value).hex() == expected_top_level
    assert codec.encode_nested(value).hex() == expected_nested


def test_u32_value_that_previously_encoded_to_five_bytes_is_rejected() -> None:
    serializer = Serializer()

    with pytest.raises(
        ValueError,
        match=(r"^value 4294967296 is out of range for U32Value; " r"expected 0 <= value <= 4294967295$"),
    ):
        serializer.serialize([U32Value(2**32)])
