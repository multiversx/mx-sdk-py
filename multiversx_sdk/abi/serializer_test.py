import pytest

from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.values_multi import *
from multiversx_sdk.abi.values_single import *


def test_serialize():
    serializer = Serializer(parts_separator="@", pub_key_length=32)

    # u8
    data = serializer.serialize([
        U8Value(0x42)
    ])

    assert data == "42"

    # u16
    data = serializer.serialize([
        U16Value(0x4243)
    ])

    assert data == "4243"

    # u8, u16
    data = serializer.serialize([
        U8Value(0x42),
        U16Value(0x4243),
    ])

    assert data == "42@4243"

    # optional (missing)
    data = serializer.serialize([
        U8Value(0x42),
        InputOptionalValue(),
    ])

    assert data == "42"

    # optional (provided)
    data = serializer.serialize([
        U8Value(0x42),
        InputOptionalValue(U8Value(0x43)),
    ])

    assert data == "42@43"

    # optional: should err because optional must be last
    with pytest.raises(ValueError, match="^an optional value must be last among input values$"):
        serializer.serialize([
            InputOptionalValue(U8Value(0x43)),
            U8Value(0x42),
        ])

    # multi<u8, u16, u32>
    data = serializer.serialize([
        InputMultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ])

    assert data == "42@4243@42434445"

    # u8, multi<u8, u16, u32>
    data = serializer.serialize([
        U8Value(0x42),
        InputMultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ])

    assert data == "42@42@4243@42434445"

    # multi<multi<u8, u16>, multi<u8, u16>>
    data = serializer.serialize([
        InputMultiValue([
            InputMultiValue([
                U8Value(0x42),
                U16Value(0x4243),
            ]),
            InputMultiValue([
                U8Value(0x44),
                U16Value(0x4445),
            ]),
        ]),
    ])

    assert data == "42@4243@44@4445"

    # variadic, of different types
    data = serializer.serialize([
        InputVariadicValues([
            U8Value(0x42),
            U16Value(0x4243),
        ]),
    ])

    # For now, the serializer does not perform such a strict type check.
    # Although doable, it would be slightly complex and, if done, might be even dropped in the future
    # (with respect to the decoder that is embedded in Rust-based smart contracts).
    assert data == "42@4243"

    # variadic<u8>, u8: should err because variadic must be last
    with pytest.raises(ValueError, match="^variadic values must be last among input values$"):
        serializer.serialize([
            InputVariadicValues([
                U8Value(0x42),
                U8Value(0x43),
            ]),
            U8Value(0x44),
        ])

    # u8, variadic<u8>
    data = serializer.serialize([
        U8Value(0x41),
        InputVariadicValues([
            U8Value(0x42),
            U8Value(0x43),
        ]),
    ])

    assert data == "41@42@43"

