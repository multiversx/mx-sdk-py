from copy import deepcopy
from typing import Any, List, cast

from multiversx_sdk.abi.abi_definition import (AbiDefinition,
                                               EndpointDefinition,
                                               ParameterDefinition)
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.interface import NativeObjectHolder
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.type_formula_parser import TypeFormulaParser
from multiversx_sdk.core.constants import ARGS_SEPARATOR


class Abi:
    def __init__(self, definition: AbiDefinition) -> None:
        self.definition = definition
        self.type_formula_parser = TypeFormulaParser()
        self.serializer = Serializer(parts_separator=ARGS_SEPARATOR)
        self.endpoints_prototypes: List[EndpointPrototype] = []

        for endpoint in definition.endpoints:
            input_prototype = self._create_endpoint_input_prototypes(endpoint)
            output_prototype = self._create_endpoint_output_prototypes(endpoint)

            endpoint_prototype = EndpointPrototype(
                name=endpoint.name,
                input_parameters=input_prototype,
                output_parameters=output_prototype
            )

            self.endpoints_prototypes.append(endpoint_prototype)

        self.endpoints_prototypes_by_name = {
            endpoint_prototype.name: endpoint_prototype
            for endpoint_prototype in self.endpoints_prototypes
        }

    def _create_endpoint_input_prototypes(self, endpoint: EndpointDefinition) -> List[Any]:
        prototypes: List[Any] = []

        for parameter in endpoint.inputs:
            parameter_prototype = self._create_parameter_prototype(parameter)
            prototypes.append(parameter_prototype)

        return prototypes

    def _create_endpoint_output_prototypes(self, endpoint: EndpointDefinition) -> List[Any]:
        prototypes: List[Any] = []

        for parameter in endpoint.outputs:
            parameter_prototype = self._create_parameter_prototype(parameter)
            prototypes.append(parameter_prototype)

        return prototypes

    def _create_parameter_prototype(self, parameter: ParameterDefinition) -> Any:
        type_formula = self.type_formula_parser.parse_expression(parameter.type)

        if type_formula.name == "BigUint":
            return BigUIntValue()
        # TODO

        raise Exception(f"unsupported type formula: {type_formula}")

    def encode_endpoint_input_parameters(self, endpoint_name: str, values: List[Any]) -> List[bytes]:
        endpoint_prototype = self._get_endpoint_prototype(endpoint_name)

        if len(values) != len(endpoint_prototype.input_parameters):
            raise ValueError(f"invalid value length: expected {len(endpoint_prototype.input_parameters)}, got {len(values)}")

        input_values = deepcopy(endpoint_prototype.input_parameters)
        input_values_as_native_object_holders = cast(List[NativeObjectHolder], input_values)

        # Populate the input values with the provided arguments
        # TODO: SKIP IF ALREADY TYPED
        for i, arg in enumerate(values):
            input_values_as_native_object_holders[i].set_native_object(arg)

        input_values_encoded = self.serializer.serialize_to_parts(input_values)
        return input_values_encoded

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: List[bytes]) -> List[Any]:
        endpoint_prototype = self._get_endpoint_prototype(endpoint_name)
        output_values = deepcopy(endpoint_prototype.output_parameters)
        self.serializer.deserialize_parts(encoded_values, output_values)

        output_values_as_native_object_holders = cast(List[NativeObjectHolder], output_values)
        output_native_values = [value.get_native_object() for value in output_values_as_native_object_holders]
        return output_native_values

    def _get_endpoint_prototype(self, endpoint_name: str) -> 'EndpointPrototype':
        endpoint_prototype = self.endpoints_prototypes_by_name.get(endpoint_name)

        if not endpoint_prototype:
            raise ValueError(f"endpoint {endpoint_name} not found")

        return endpoint_prototype


class EndpointPrototype:
    def __init__(self, name: str, input_parameters: List[Any], output_parameters: List[Any]) -> None:
        self.name = name
        self.input_parameters = input_parameters
        self.output_parameters = output_parameters
