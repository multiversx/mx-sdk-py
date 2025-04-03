from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from multiversx_sdk.abi.abi_definition import (
    AbiDefinition,
    EndpointDefinition,
    EnumDefinition,
    EventDefinition,
    EventTopicDefinition,
    ParameterDefinition,
    StructDefinition,
)
from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.array_value import ArrayValue
from multiversx_sdk.abi.bigint_value import BigIntValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.bool_value import BoolValue
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.abi.counted_variadic_values import CountedVariadicValues
from multiversx_sdk.abi.enum_value import EnumValue
from multiversx_sdk.abi.explicit_enum_value import ExplicitEnumValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.interface import IPayloadHolder, ISingleValue
from multiversx_sdk.abi.list_value import ListValue
from multiversx_sdk.abi.managed_decimal_signed_value import ManagedDecimalSignedValue
from multiversx_sdk.abi.managed_decimal_value import ManagedDecimalValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.option_value import OptionValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import (
    I8Value,
    I16Value,
    I32Value,
    I64Value,
    U8Value,
    U16Value,
    U32Value,
    U64Value,
)
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.struct_value import StructValue
from multiversx_sdk.abi.token_identifier_value import TokenIdentifierValue
from multiversx_sdk.abi.tuple_value import TupleValue
from multiversx_sdk.abi.type_formula import TypeFormula
from multiversx_sdk.abi.type_formula_parser import TypeFormulaParser
from multiversx_sdk.abi.variadic_values import VariadicValues


class Abi:
    def __init__(self, definition: AbiDefinition) -> None:
        self._type_formula_parser = TypeFormulaParser()
        self._serializer = Serializer()

        self.definition = definition
        self.custom_types_prototypes_by_name: dict[str, Any] = {}
        self.endpoints_prototypes_by_name: dict[str, EndpointPrototype] = {}
        self.events_prototypes_by_name: dict[str, EventPrototype] = {}

        for name in definition.types.enums:
            self.custom_types_prototypes_by_name[name] = self._create_custom_type_prototype(name)

        for struct_type in definition.types.structs:
            self.custom_types_prototypes_by_name[struct_type] = self._create_custom_type_prototype(struct_type)

        self.constructor_prototype = EndpointPrototype(
            input_parameters=self._create_endpoint_input_prototypes(definition.constructor),
            output_parameters=self._create_endpoint_output_prototypes(definition.constructor),
        )

        self.upgrade_constructor_prototype = EndpointPrototype(
            input_parameters=self._create_endpoint_input_prototypes(definition.upgrade_constructor),
            output_parameters=self._create_endpoint_output_prototypes(definition.upgrade_constructor),
        )

        for endpoint in definition.endpoints:
            input_prototype = self._create_endpoint_input_prototypes(endpoint)
            output_prototype = self._create_endpoint_output_prototypes(endpoint)

            endpoint_prototype = EndpointPrototype(input_parameters=input_prototype, output_parameters=output_prototype)

            self.endpoints_prototypes_by_name[endpoint.name] = endpoint_prototype

        for event in definition.events:
            prototype = self._create_event_input_prototypes(event)

            event_prototype = EventPrototype(fields=prototype)

            self.events_prototypes_by_name[event.identifier] = event_prototype

    def _create_custom_type_prototype(self, name: str) -> Any:
        if name in self.definition.types.enums:
            definition = self.definition.types.enums[name]
            return self._create_enum_prototype(definition)
        if name in self.definition.types.explicit_enums:
            definition = self.definition.types.explicit_enums[name]
            return self._create_explicit_enum_prototype()
        if name in self.definition.types.structs:
            definition = self.definition.types.structs[name]
            return self._create_struct_prototype(definition)

        raise ValueError(f"cannot create prototype for custom type {name}: definition not found")

    def _create_enum_prototype(self, enum_definition: EnumDefinition) -> Any:
        return EnumValue(
            fields_provider=lambda discriminant: self._provide_fields_for_enum_prototype(discriminant, enum_definition),
            names_to_discriminants={v.name: v.discriminant for v in enum_definition.variants},
        )

    def _create_explicit_enum_prototype(self) -> Any:
        return ExplicitEnumValue()

    def _provide_fields_for_enum_prototype(self, discriminant: int, enum_definition: EnumDefinition) -> list[Field]:
        for variant in enum_definition.variants:
            if variant.discriminant != discriminant:
                continue

            fields_prototypes: list[Field] = []

            for field_definition in variant.fields:
                type_formula = self._type_formula_parser.parse_expression(field_definition.type)
                field_value_prototype = self._create_prototype(type_formula)
                field_prototype = Field(name=field_definition.name, value=field_value_prototype)
                fields_prototypes.append(field_prototype)

            return fields_prototypes

        raise ValueError(
            f"cannot provide fields from enum {enum_definition.name}: variant with discriminant {discriminant} not found"
        )

    def _create_struct_prototype(self, struct_definition: StructDefinition) -> Any:
        fields_prototypes: list[Field] = []

        for field_definition in struct_definition.fields:
            type_formula = self._type_formula_parser.parse_expression(field_definition.type)
            field_value_prototype = self._create_prototype(type_formula)
            field_prototype = Field(name=field_definition.name, value=field_value_prototype)
            fields_prototypes.append(field_prototype)

        return StructValue(fields_prototypes)

    def _create_endpoint_input_prototypes(self, endpoint: EndpointDefinition) -> list[Any]:
        prototypes: list[Any] = []

        for parameter in endpoint.inputs:
            parameter_prototype = self._create_parameter_prototype(parameter)
            prototypes.append(parameter_prototype)

        return prototypes

    def _create_endpoint_output_prototypes(self, endpoint: EndpointDefinition) -> list[Any]:
        prototypes: list[Any] = []

        for parameter in endpoint.outputs:
            parameter_prototype = self._create_parameter_prototype(parameter)
            prototypes.append(parameter_prototype)

        return prototypes

    def _create_event_input_prototypes(self, event: EventDefinition) -> list[Any]:
        prototypes: list[Any] = []

        for topic in event.inputs:
            event_field_prototype = EventField(name=topic.name, value=self._create_event_field_prototype(topic))
            prototypes.append(event_field_prototype)

        return prototypes

    def _create_parameter_prototype(self, parameter: ParameterDefinition) -> Any:
        type_formula = self._type_formula_parser.parse_expression(parameter.type)
        return self._create_prototype(type_formula)

    def _create_event_field_prototype(self, parameter: EventTopicDefinition) -> Any:
        type_formula = self._type_formula_parser.parse_expression(parameter.type)
        return self._create_prototype(type_formula)

    def encode_constructor_input_parameters(self, values: list[Any]) -> list[bytes]:
        return self._do_encode_endpoint_input_parameters("constructor", self.constructor_prototype, values)

    def encode_upgrade_constructor_input_parameters(self, values: list[Any]) -> list[bytes]:
        return self._do_encode_endpoint_input_parameters("upgrade", self.upgrade_constructor_prototype, values)

    def encode_endpoint_input_parameters(self, endpoint_name: str, values: list[Any]) -> list[bytes]:
        endpoint_prototype = self._get_endpoint_prototype(endpoint_name)
        return self._do_encode_endpoint_input_parameters(endpoint_name, endpoint_prototype, values)

    def _do_encode_endpoint_input_parameters(
        self,
        endpoint_name: str,
        endpoint_prototype: "EndpointPrototype",
        values: list[Any],
    ):
        if len(values) != len(endpoint_prototype.input_parameters):
            raise ValueError(
                f"for {endpoint_name}, invalid value length: expected {len(endpoint_prototype.input_parameters)}, got {len(values)}"
            )

        input_values = deepcopy(endpoint_prototype.input_parameters)
        input_values_as_native_object_holders = cast(list[IPayloadHolder], input_values)

        # Populate the input values with the provided arguments
        for i, arg in enumerate(values):
            input_values_as_native_object_holders[i].set_payload(arg)

        input_values_encoded = self._serializer.serialize_to_parts(input_values)
        return input_values_encoded

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: list[bytes]) -> list[Any]:
        endpoint_prototype = self._get_endpoint_prototype(endpoint_name)
        output_values = deepcopy(endpoint_prototype.output_parameters)
        self._serializer.deserialize_parts(encoded_values, output_values)

        output_values_as_native_object_holders = cast(list[IPayloadHolder], output_values)
        output_native_values = [value.get_payload() for value in output_values_as_native_object_holders]
        return output_native_values

    def decode_event(self, event_name: str, topics: list[bytes], additional_data: list[bytes]) -> SimpleNamespace:
        result = SimpleNamespace()
        event_definition = self.definition.get_event_definition(event_name)
        event_prototype = self._get_event_prototype(event_name)

        indexed_inputs = [input for input in event_definition.inputs if input.indexed]
        indexed_inputs_names = [item.name for item in indexed_inputs]

        fields = deepcopy(event_prototype.fields)

        output_values = [field.value for field in fields if field.name in indexed_inputs_names]
        self._serializer.deserialize_parts(topics, output_values)

        output_values_as_native_object_holders = cast(list[IPayloadHolder], output_values)
        output_native_values = [value.get_payload() for value in output_values_as_native_object_holders]

        for i in range(len(indexed_inputs)):
            setattr(result, indexed_inputs[i].name, output_native_values[i])

        non_indexed_inputs = [input for input in event_definition.inputs if not input.indexed]
        non_indexed_inputs_names = [item.name for item in non_indexed_inputs]

        output_values = [field.value for field in fields if field.name in non_indexed_inputs_names]
        self._serializer.deserialize_parts(additional_data, output_values)

        output_values_as_native_object_holders = cast(list[IPayloadHolder], output_values)
        output_native_values = [value.get_payload() for value in output_values_as_native_object_holders]

        for i in range(len(non_indexed_inputs)):
            setattr(result, non_indexed_inputs[i].name, output_native_values[i])

        return result

    def encode_custom_type(self, name: str, values: list[Any]):
        try:
            custom_type: IPayloadHolder = self.custom_types_prototypes_by_name[name]
        except KeyError:
            raise Exception(f'Missing custom type! No custom type found for name: "{name}"')

        custom_type.set_payload(values)
        return self._serializer.serialize([custom_type])

    def decode_custom_type(self, name: str, data: bytes) -> Any:
        try:
            custom_type: ISingleValue = self.custom_types_prototypes_by_name[name]
        except KeyError:
            raise Exception(f'Missing custom type! No custom type found for name: "{name}"')

        custom_type.decode_top_level(data)
        return custom_type.get_payload()

    def _get_custom_type_prototype(self, type_name: str) -> Any:
        type_prototype = self.custom_types_prototypes_by_name.get(type_name)

        if not type_prototype:
            return self._create_custom_type_prototype(type_name)

        return type_prototype

    def _get_endpoint_prototype(self, endpoint_name: str) -> "EndpointPrototype":
        endpoint_prototype = self.endpoints_prototypes_by_name.get(endpoint_name)

        if not endpoint_prototype:
            raise ValueError(f"endpoint '{endpoint_name}' not found")

        return endpoint_prototype

    def _get_event_prototype(self, event_name: str) -> "EventPrototype":
        event_prototype = self.events_prototypes_by_name.get(event_name)

        if not event_prototype:
            raise ValueError(f"event '{event_name}' not found")

        return event_prototype

    def _create_prototype(self, type_formula: TypeFormula) -> Any:
        name = type_formula.name

        if name == "bool":
            return BoolValue()
        if name == "u8":
            return U8Value()
        if name == "u16":
            return U16Value()
        if name == "u32":
            return U32Value()
        if name == "u64":
            return U64Value()
        if name == "i8":
            return I8Value()
        if name == "i16":
            return I16Value()
        if name == "i32":
            return I32Value()
        if name == "i64":
            return I64Value()
        if name == "BigUint":
            return BigUIntValue()
        if name == "BigInt":
            return BigIntValue()
        if name == "bytes":
            return BytesValue()
        if name == "utf-8 string":
            return StringValue()
        if name == "Address":
            return AddressValue()
        if name == "TokenIdentifier":
            return TokenIdentifierValue()
        if name == "EgldOrEsdtTokenIdentifier":
            return TokenIdentifierValue()
        if name == "CodeMetadata":
            return CodeMetadataValue()
        if name == "tuple":
            return TupleValue(
                [self._create_prototype(type_parameter) for type_parameter in type_formula.type_parameters]
            )
        if name == "Option":
            type_parameter = type_formula.type_parameters[0]
            return OptionValue(self._create_prototype(type_parameter))
        if name == "List":
            type_parameter = type_formula.type_parameters[0]
            return ListValue([], item_creator=lambda: self._create_prototype(type_parameter))
        if name.startswith("array"):
            type_parameter = type_formula.type_parameters[0]
            length = int(name[5:])
            return ArrayValue(
                length=length,
                item_creator=lambda: self._create_prototype(type_parameter),
            )
        if name == "optional":
            # The prototype of an optional is provided a value (the placeholder).
            type_parameter = type_formula.type_parameters[0]
            return OptionalValue(self._create_prototype(type_parameter))
        if name == "variadic":
            type_parameter = type_formula.type_parameters[0]
            return VariadicValues([], item_creator=lambda: self._create_prototype(type_parameter))
        if name == "counted-variadic":
            type_parameter = type_formula.type_parameters[0]
            return CountedVariadicValues([], item_creator=lambda: self._create_prototype(type_parameter))
        if name == "multi":
            return MultiValue(
                [self._create_prototype(type_parameter) for type_parameter in type_formula.type_parameters]
            )
        if name == "ManagedDecimal":
            scale = type_formula.type_parameters[0].name

            if scale == "usize":
                return ManagedDecimalValue(scale=0, is_variable=True)
            else:
                return ManagedDecimalValue(scale=int(scale), is_variable=False)
        if name == "ManagedDecimalSigned":
            scale = type_formula.type_parameters[0].name

            if scale == "usize":
                return ManagedDecimalSignedValue(scale=0, is_variable=True)
            else:
                return ManagedDecimalSignedValue(scale=int(scale), is_variable=False)

        # Handle custom types
        type_prototype = self._get_custom_type_prototype(name)
        return deepcopy(type_prototype)

    @classmethod
    def load(cls, path: Path) -> "Abi":
        definition = AbiDefinition.load(path)
        return cls(definition)


class EndpointPrototype:
    def __init__(self, input_parameters: list[Any], output_parameters: list[Any]) -> None:
        self.input_parameters = input_parameters
        self.output_parameters = output_parameters


class EventField:
    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value


class EventPrototype:
    def __init__(self, fields: list[EventField]) -> None:
        self.fields = fields
