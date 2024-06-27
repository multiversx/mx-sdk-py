from typing import cast

import pytest

from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.counted_variadic_values import CountedVariadicValues
from multiversx_sdk.abi.enum_value import EnumValue
from multiversx_sdk.abi.fields import *
from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.multi_value import *
from multiversx_sdk.abi.option_value import OptionValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import *
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.struct_value import StructValue
from multiversx_sdk.abi.variadic_values import VariadicValues

alice_pub_key = bytes.fromhex("0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1")
bob_pub_key = bytes.fromhex("8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8")
one_quintillion = 1_000_000_000_000_000_000


def test_serialize():
    serializer = Serializer(parts_separator="@")

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
        OptionalValue(),
    ])

    assert data == "42"

    # optional (provided)
    data = serializer.serialize([
        U8Value(0x42),
        OptionalValue(U8Value(0x43)),
    ])

    assert data == "42@43"

    # optional: should err because optional must be last
    with pytest.raises(ValueError, match="^an optional value must be last among input values$"):
        serializer.serialize([
            OptionalValue(U8Value(0x43)),
            U8Value(0x42),
        ])

    # multi<u8, u16, u32>
    data = serializer.serialize([
        MultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ])

    assert data == "42@4243@42434445"

    # u8, multi<u8, u16, u32>
    data = serializer.serialize([
        U8Value(0x42),
        MultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ])

    assert data == "42@42@4243@42434445"

    # multi<multi<u8, u16>, multi<u8, u16>>
    data = serializer.serialize([
        MultiValue([
            MultiValue([
                U8Value(0x42),
                U16Value(0x4243),
            ]),
            MultiValue([
                U8Value(0x44),
                U16Value(0x4445),
            ]),
        ]),
    ])

    assert data == "42@4243@44@4445"

    # variadic, of different types
    data = serializer.serialize([
        VariadicValues([
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
            VariadicValues([
                U8Value(0x42),
                U8Value(0x43),
            ]),
            U8Value(0x44),
        ])

    # u8, variadic<u8>
    data = serializer.serialize([
        U8Value(0x41),
        VariadicValues([
            U8Value(0x42),
            U8Value(0x43),
        ]),
    ])

    assert data == "41@42@43"

    # counted-variadic, of different types
    data = serializer.serialize([
        CountedVariadicValues(
            items=[
                U8Value(0x42),
                U16Value(0x4243),
            ]),
    ])
    assert data == "02@42@4243"

    # variadic<u8>
    data = serializer.serialize([
        CountedVariadicValues(
            items=[
                U8Value(0x42),
                U8Value(0x43),
            ]),
        U8Value(0x44),
    ])
    assert data == "02@42@43@44"


def test_deserialize():
    serializer = Serializer(parts_separator="@")

    # nil destination
    with pytest.raises(ValueError, match="^cannot deserialize into null value$"):
        serializer.deserialize("", [None])

    # u8
    output_values = [
        U8Value(),
    ]

    serializer.deserialize("42", output_values)

    assert output_values == [
        U8Value(0x42),
    ]

    # u16
    output_values = [
        U16Value(),
    ]

    serializer.deserialize("4243", output_values)

    assert output_values == [
        U16Value(0x4243),
    ]

    # u8, u16
    output_values = [
        U8Value(),
        U16Value(),
    ]

    serializer.deserialize("42@4243", output_values)

    assert output_values == [
        U8Value(0x42),
        U16Value(0x4243),
    ]

    # u8, u16
    output_values = [
        U8Value(),
        U16Value(),
    ]

    with pytest.raises(Exception, match="not all parts have been deserialized"):
        serializer.deserialize("42@4243@44", output_values)

    # optional (missing)
    output_values = [
        U8Value(),
        OptionalValue(U8Value()),
    ]

    serializer.deserialize("42", output_values)

    assert output_values == [
        U8Value(0x42),
        OptionalValue(value=None),
    ]

    # optional (provided)
    output_values = [
        U8Value(),
        OptionalValue(U8Value()),
    ]

    serializer.deserialize("42@43", output_values)

    assert output_values == [
        U8Value(0x42),
        OptionalValue(U8Value(0x43)),
    ]

    # optional: should err because optional must be last
    with pytest.raises(ValueError, match="^an optional value must be last among output values$"):
        output_values = [
            OptionalValue(U8Value()),
            U8Value(),
        ]

        serializer.deserialize("43@42", output_values)

    # multi<u8, u16, u32>
    output_values = [
        MultiValue([
            U8Value(),
            U16Value(),
            U32Value(),
        ]),
    ]

    serializer.deserialize("42@4243@42434445", output_values)

    assert output_values == [
        MultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ]

    # u8, multi<u8, u16, u32>
    output_values = [
        U8Value(),
        MultiValue([
            U8Value(),
            U16Value(),
            U32Value(),
        ]),
    ]

    serializer.deserialize("42@42@4243@42434445", output_values)

    assert output_values == [
        U8Value(0x42),
        MultiValue([
            U8Value(0x42),
            U16Value(0x4243),
            U32Value(0x42434445),
        ]),
    ]

    # empty: u8
    destination = VariadicValues(
        item_creator=lambda: U8Value()
    )

    serializer.deserialize("", [destination])

    assert destination.items == [U8Value(0)]

    # variadic<u8>
    destination = VariadicValues(
        item_creator=lambda: U8Value()
    )

    serializer.deserialize("2A@2B@2C", [destination])

    assert destination.items == [
        U8Value(0x2A),
        U8Value(0x2B),
        U8Value(0x2C),
    ]

    # variadic<u8>, with empty items
    destination = VariadicValues(
        item_creator=lambda: U8Value()
    )

    serializer.deserialize("@01@00@", [destination])

    assert destination.items == [
        U8Value(0x00),
        U8Value(0x01),
        U8Value(0x00),
        U8Value(0x00),
    ]

    # variadic<u32>
    destination = VariadicValues(
        item_creator=lambda: U32Value()
    )

    serializer.deserialize("AABBCCDD@DDCCBBAA", [destination])

    assert destination.items == [
        U32Value(0xAABBCCDD),
        U32Value(0xDDCCBBAA),
    ]

    # variadic<u8>, u8: should err because decoded value is too large
    with pytest.raises(ValueError, match="^cannot decode \\(top-level\\) U8Value, because of: decoded value is too large or invalid \\(does not fit into 1 byte\\(s\\)\\): 256$"):
        destination = VariadicValues(
            item_creator=lambda: U8Value()
        )

        serializer.deserialize("0100", [destination])

    # # counted-variadic<u32>, variadic<u32>
    destination = [CountedVariadicValues(item_creator=lambda: U32Value()), VariadicValues(item_creator=lambda: U32Value())]

    serializer.deserialize("03@41@42@43@44@45", destination)
    assert len(destination) == 2

    assert isinstance(destination[0], CountedVariadicValues)
    assert destination[0].length == 3
    assert destination[0].items == [
        U32Value(0x41),
        U32Value(0x42),
        U32Value(0x43),
    ]

    assert isinstance(destination[1], VariadicValues)
    assert destination[1].items == [
        U32Value(0x44),
        U32Value(0x45)
    ]

    # counted-variadic<u8>
    destination = CountedVariadicValues(
        item_creator=lambda: U8Value()
    )

    serializer.deserialize("03@2A@2B@2C", [destination])
    assert destination.length == 3
    assert destination.items == [
        U8Value(0x2A),
        U8Value(0x2B),
        U8Value(0x2C),
    ]

    # counted-variadic<u8>, with empty items
    destination = CountedVariadicValues(
        item_creator=lambda: U8Value()
    )

    serializer.deserialize("04@@01@00@", [destination])

    assert destination.length == 4
    assert destination.items == [
        U8Value(0x00),
        U8Value(0x01),
        U8Value(0x00),
        U8Value(0x00),
    ]

    # variadic<u32>
    destination = CountedVariadicValues(
        item_creator=lambda: U32Value()
    )

    serializer.deserialize("02@AABBCCDD@DDCCBBAA", [destination])

    assert destination.length == 2
    assert destination.items == [
        U32Value(0xAABBCCDD),
        U32Value(0xDDCCBBAA),
    ]


def test_real_world_multisig_propose_batch():
    """
    serialize input of multisig.proposeBatch(variadic<Action>
    """

    serializer = Serializer(parts_separator="@")

    def create_esdt_token_payment(token_identifier: str, token_nonce: int, amount: int) -> StructValue:
        return StructValue([
            Field("token_identifier", StringValue(token_identifier)),
            Field("token_nonce", U64Value(token_nonce)),
            Field("amount", BigUIntValue(amount)),
        ])

    # First action: SendTransferExecuteEgld
    first_action = EnumValue(
        discriminant=5,
        fields=[
            Field("to", AddressValue(alice_pub_key)),
            Field("egld_amount", BigUIntValue(one_quintillion)),
            Field("opt_gas_limit", OptionValue(U64Value(15_000_000))),
            Field("endpoint_name", BytesValue(b"example")),
            Field("arguments", ListValue([
                BytesValue(bytes([0x03, 0x42])),
                BytesValue(bytes([0x07, 0x43])),
            ])),
        ],
    )

    # Second action: SendTransferExecuteEsdt
    second_action = EnumValue(
        discriminant=6,
        fields=[
            Field("to", AddressValue(alice_pub_key)),
            Field("tokens", ListValue([
                create_esdt_token_payment("beer", 0, one_quintillion),
                create_esdt_token_payment("chocolate", 0, one_quintillion),
            ])),
            Field("opt_gas_limit", OptionValue(U64Value(15_000_000))),
            Field("endpoint_name", BytesValue(b"example")),
            Field("arguments", ListValue([
                BytesValue(bytes([0x03, 0x42])),
                BytesValue(bytes([0x07, 0x43])),
            ])),
        ],
    )

    data = serializer.serialize([
        first_action,
        second_action,
    ])

    data_expected = "@".join([
        "05|0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1|000000080de0b6b3a7640000|010000000000e4e1c0|000000076578616d706c65|00000002000000020342000000020743",
        "06|0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1|00000002|0000000462656572|0000000000000000|000000080de0b6b3a7640000|0000000963686f636f6c617465|0000000000000000|000000080de0b6b3a7640000|010000000000e4e1c0|000000076578616d706c65|00000002000000020342000000020743",
    ])

    # Drop the delimiters (were added for readability)
    data_expected = data_expected.replace("|", "")

    assert data == data_expected


def test_real_world_multisig_get_pending_action_full_info():
    """
    deserialize output of multisig.getPendingActionFullInfo() -> variadic<ActionFullInfo>
    """

    serializer = Serializer(parts_separator="@")

    data_hex = "".join([
        "0000002A",
        "0000002A",
        "05|0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1|000000080de0b6b3a7640000|010000000000e4e1c0|000000076578616d706c65|00000002000000020342000000020743",
        "00000002|0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1|8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8",
    ])

    # Drop the delimiters (were added for readability)
    data = data_hex.replace("|", "")

    action_id = U32Value()
    group_id = U32Value()

    action_to = AddressValue()
    action_egld_amount = BigUIntValue()
    action_gas_limit = U64Value()
    action_endpoint_name = BytesValue()
    action_arguments = ListValue(
        item_creator=lambda: BytesValue()
    )

    def action_fields_provider(discriminant: int) -> List[Field]:
        if discriminant == 5:
            return [
                Field("to", action_to),
                Field("egld_amount", action_egld_amount),
                Field("opt_gas_limit", OptionValue(action_gas_limit)),
                Field("endpoint_name", action_endpoint_name),
                Field("arguments", action_arguments),
            ]

        return []

    action = EnumValue(
        fields_provider=action_fields_provider
    )

    signers = ListValue(
        item_creator=lambda: AddressValue()
    )

    destination = VariadicValues(
        item_creator=lambda: StructValue([
            Field("action_id", action_id),
            Field("group_id", group_id),
            Field("action_data", action),
            Field("signers", signers),
        ]),
    )

    serializer.deserialize(data, [destination])

    assert len(destination.items) == 1

    # result[0].action_id and result[0].group_id
    assert action_id.value == 42
    assert group_id.value == 42

    # result[0].action_data
    assert action.discriminant == 5
    assert action_to.value == alice_pub_key
    assert action_egld_amount.value == one_quintillion
    assert action_gas_limit.value == 15_000_000
    assert action_endpoint_name.value == b"example"
    assert len(action_arguments.items) == 2
    assert cast(BytesValue, action_arguments.items[0]).value == bytes([0x03, 0x42])
    assert cast(BytesValue, action_arguments.items[1]).value == bytes([0x07, 0x43])

    # result[0].signers
    assert cast(AddressValue, signers.items[0]).value == alice_pub_key
    assert cast(AddressValue, signers.items[1]).value == bob_pub_key
