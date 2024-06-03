import json
from pathlib import Path
from typing import Any, Dict, List


class ParameterDefinition:
    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParameterDefinition':
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
        )

    def __repr__(self):
        return f"ParameterDefinition(name={self.name}, type={self.type})"

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, ParameterDefinition)
            and self.name == value.name
            and self.type == value.type
        )


class FieldDefinition:
    def __init__(self,
                 name: str,
                 description: str,
                 type: str) -> None:
        self.name = name
        self.description = description
        self.type = type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldDefinition':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=data.get("type", "")
        )

    def __repr__(self):
        return f"FieldDefinition(name={self.name}, type={self.type})"


class EnumVariantDefinition:
    def __init__(self,
                 name: str,
                 discriminant: int,
                 fields: List[FieldDefinition]) -> None:
        self.name = name
        self.discriminant = discriminant
        self.fields = fields

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnumVariantDefinition':
        fields = [FieldDefinition.from_dict(item) for item in data.get("fields", [])]

        return cls(
            name=data.get("name", ""),
            discriminant=data.get("discriminant", 0),
            fields=fields
        )

    def __repr__(self):
        return f"EnumVariantDefinition(name={self.name}, discriminant={self.discriminant})"


class EnumDefinition:
    def __init__(self,
                 name: str,
                 variants: List[EnumVariantDefinition]) -> None:
        self.name = name
        self.variants = variants

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'EnumDefinition':
        variants = [EnumVariantDefinition.from_dict(item) for item in data["variants"]]

        return cls(
            name=name,
            variants=variants
        )

    def __repr__(self):
        return f"EnumDefinition(name={self.name})"


class StructDefinition:
    def __init__(self,
                 name: str,
                 fields: List[FieldDefinition]) -> None:
        self.name = name
        self.fields = fields

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'StructDefinition':
        fields = [FieldDefinition.from_dict(item) for item in data["fields"]]

        return cls(
            name=name,
            fields=fields
        )

    def __repr__(self):
        return f"StructDefinition(name={self.name})"


class EventTopicDefinition:
    def __init__(self,
                 name: str,
                 type: str,
                 indexed: bool) -> None:
        self.name = name
        self.type = type
        self.indexed = indexed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventTopicDefinition':
        return cls(
            name=data["name"],
            type=data["type"],
            indexed=data["indexed"]
        )

    def __repr__(self):
        return f"EventTopicDefinition(name={self.name})"


class EventDefinition:
    def __init__(self,
                 identifier: str,
                 inputs: List[EventTopicDefinition]) -> None:
        self.identifier = identifier
        self.inputs = inputs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventDefinition':
        inputs = [EventTopicDefinition.from_dict(item) for item in data["inputs"]]

        return cls(
            identifier=data["identifier"],
            inputs=inputs
        )

    def __repr__(self):
        return f"EventDefinition(identifier={self.identifier})"


class EndpointDefinition:
    def __init__(self,
                 name: str,
                 mutability: str,
                 inputs: List[ParameterDefinition],
                 outputs: List[ParameterDefinition],
                 payable_in_tokens: List[str],
                 only_owner: bool) -> None:
        self.name = name
        self.mutability = mutability
        self.inputs = inputs
        self.outputs = outputs
        self.payable_in_tokens = payable_in_tokens
        self.only_owner = only_owner

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EndpointDefinition':
        inputs = [ParameterDefinition.from_dict(item) for item in data["inputs"]]
        outputs = [ParameterDefinition.from_dict(item) for item in data["outputs"]]

        return cls(
            name=data.get("name", ""),
            mutability=data.get("mutability", ""),
            inputs=inputs,
            outputs=outputs,
            payable_in_tokens=data.get("payableInTokens", []),
            only_owner=data.get("onlyOwner", False)
        )

    def __repr__(self):
        return f"EndpointDefinition(name={self.name})"


class TypesDefinitions:
    def __init__(self,
                 enums: List[EnumDefinition],
                 structs: List[StructDefinition]) -> None:
        self.enums: Dict[str, EnumDefinition] = {enum.name: enum for enum in enums}
        self.structs: Dict[str, StructDefinition] = {struct.name: struct for struct in structs}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TypesDefinitions':
        enums: List[EnumDefinition] = []
        structs: List[StructDefinition] = []

        for name, definition in data.items():
            kind = definition["type"]

            if kind == "enum":
                enums.append(EnumDefinition.from_dict(name, definition))
            elif kind == "struct":
                structs.append(StructDefinition.from_dict(name, definition))
            else:
                raise ValueError(f"Unsupported kind of custom type: {kind}")

        return cls(
            enums=enums,
            structs=structs
        )


class AbiDefinition:
    def __init__(self,
                 constructor: EndpointDefinition,
                 upgrade_constructor: EndpointDefinition,
                 endpoints: List[EndpointDefinition],
                 types: TypesDefinitions) -> None:
        self.constructor = constructor
        self.upgrade_constructor = upgrade_constructor
        self.endpoints = endpoints
        self.types = types

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AbiDefinition':
        constructor = EndpointDefinition.from_dict(data["constructor"])
        constructor.name = "constructor"

        upgrade_constructor = cls._get_endpoint_for_upgrade(data)
        upgrade_constructor.name = "upgrade_constructor"

        endpoints = [EndpointDefinition.from_dict(item) for item in data["endpoints"]] if "endpoints" in data else []
        types = TypesDefinitions.from_dict(data.get("types", {}))

        return cls(
            constructor=constructor,
            upgrade_constructor=upgrade_constructor,
            endpoints=endpoints,
            types=types
        )

    @classmethod
    def _get_endpoint_for_upgrade(cls, data: Dict[str, Any]) -> EndpointDefinition:
        if "upgradeConstructor" in data:
            return EndpointDefinition.from_dict(data["upgradeConstructor"])

        # Fallback for contracts written using a not-old, but not-new Rust framework:
        if "upgrade" in data["endpoints"]:
            return EndpointDefinition.from_dict(data["endpoints"]["upgrade"])

        # Fallback for contracts written using an old Rust framework:
        return EndpointDefinition.from_dict(data["constructor"])

    @classmethod
    def load(cls, path: Path) -> 'AbiDefinition':
        content = Path(path).read_text()
        data = json.loads(content)
        return cls.from_dict(data)
