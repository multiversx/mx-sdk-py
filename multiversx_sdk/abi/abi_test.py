from pathlib import Path

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.abi_definition import (AbiDefinition,
                                               ParameterDefinition)
from multiversx_sdk.abi.biguint_value import BigUIntValue

testdata = Path(__file__).parent.parent / "testutils" / "testdata"


def test_abi():
    abi_path = testdata / "adder.abi.json"
    abi_definition = AbiDefinition.load(abi_path)
    abi = Abi(abi_definition)

    assert abi.definition.constructor.name == "constructor"
    assert abi.definition.constructor.inputs == [ParameterDefinition("initial_value", "BigUint")]
    assert abi.definition.constructor.outputs == []

    assert abi.definition.upgrade_constructor.name == "upgrade_constructor"
    assert abi.definition.upgrade_constructor.inputs == [ParameterDefinition("initial_value", "BigUint")]
    assert abi.definition.upgrade_constructor.outputs == []

    assert abi.definition.endpoints[0].name == "getSum"
    assert abi.definition.endpoints[0].inputs == []
    assert abi.definition.endpoints[0].outputs == [ParameterDefinition("", "BigUint")]

    assert abi.definition.endpoints[1].name == "add"
    assert abi.definition.endpoints[1].inputs == [ParameterDefinition("value", "BigUint")]
    assert abi.definition.endpoints[1].outputs == []

    assert abi.definition.types.enums == {}
    assert abi.definition.types.structs == {}
    assert abi.custom_types_prototypes_by_name == {}

    assert abi.constructor_prototype.input_parameters == [BigUIntValue()]
    assert abi.constructor_prototype.output_parameters == []
    assert abi.upgrade_constructor_prototype.input_parameters == [BigUIntValue()]
    assert abi.upgrade_constructor_prototype.output_parameters == []

    assert abi.endpoints_prototypes_by_name["getSum"].input_parameters == []
    assert abi.endpoints_prototypes_by_name["getSum"].output_parameters == [BigUIntValue()]
    assert abi.endpoints_prototypes_by_name["add"].input_parameters == [BigUIntValue()]
    assert abi.endpoints_prototypes_by_name["add"].output_parameters == []
