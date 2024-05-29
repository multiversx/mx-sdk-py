from copy import deepcopy
from pathlib import Path
from typing import List

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.abi_definition import AbiDefinition
from multiversx_sdk.abi.enum_value import EnumValue
from multiversx_sdk.abi.field import Field
from multiversx_sdk.abi.small_int_values import U8Value

testdata = Path(__file__).parent.parent / "testutils" / "testdata"


def test_abi():
    abi_path = testdata / "adder.abi.json"
    abi_definition = AbiDefinition.load(abi_path)
    abi = Abi(abi_definition)


if __name__ == "__main__":
    test_abi()

    def action_fields_provider(discriminant: int) -> List[Field]:
        if discriminant == 5:
            return [
                Field("foo", U8Value()),
            ]

        return []

    action = EnumValue(
        discriminant=7,
        fields_provider=action_fields_provider,
        fields=[
            Field("bar", U8Value()),
        ]
    )
