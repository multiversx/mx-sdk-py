import json
from pathlib import Path
from typing import Any


class AbiDefinition:
    def __init__(
        self,
        constructor: "EndpointDefinition",
        upgrade_constructor: "EndpointDefinition",
        endpoints: list["EndpointDefinition"],
        types: "TypesDefinitions",
        events: list["EventDefinition"],
    ) -> None:
        self.constructor = constructor
        self.upgrade_constructor = upgrade_constructor
        self.endpoints = endpoints
        self.types = types
        self.events = events

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AbiDefinition":
        constructor = cls._get_definition_for_constructor(data)
        constructor.name = "constructor"

        upgrade_constructor = cls._get_definition_for_upgrade(data)
        upgrade_constructor.name = "upgrade_constructor"

        endpoints = [EndpointDefinition.from_dict(item) for item in data["endpoints"]] if "endpoints" in data else []
        types = TypesDefinitions.from_dict(data.get("types", {}))

        events = [EventDefinition.from_dict(item) for item in data["events"]] if "events" in data else []

        return cls(
            constructor=constructor,
            upgrade_constructor=upgrade_constructor,
            endpoints=endpoints,
            types=types,
            events=events,
        )

    @classmethod
    def _get_definition_for_constructor(cls, data: dict[str, Any]):
        if "constructor" in data:
            return EndpointDefinition.from_dict(data["constructor"])

        return NullEndpointDefinition()

    @classmethod
    def _get_definition_for_upgrade(cls, data: dict[str, Any]) -> "EndpointDefinition":
        if "upgradeConstructor" in data:
            return EndpointDefinition.from_dict(data["upgradeConstructor"])

        # Fallback for contracts written using a not-old, but not-new Rust framework:
        endpoints = data.get("endpoints", [])
        if "upgrade" in endpoints:
            return EndpointDefinition.from_dict(data["endpoints"]["upgrade"])

        # Fallback for contracts written using an old Rust framework:
        if "constructor" in data:
            EndpointDefinition.from_dict(data["constructor"])

        return NullEndpointDefinition()

    @classmethod
    def load(cls, path: Path) -> "AbiDefinition":
        content = Path(path).read_text()
        data = json.loads(content)
        return cls.from_dict(data)

    def get_event_definition(self, name: str) -> "EventDefinition":
        event = [event for event in self.events if event.identifier == name]

        if not len(event):
            raise Exception(f"event [{name}] not found")

        if len(event) > 1:
            raise Exception(f"more than one event found: [{event}]")

        return event[0]


class EndpointDefinition:
    def __init__(
        self,
        name: str,
        docs: str,
        mutability: str,
        inputs: list["ParameterDefinition"],
        outputs: list["ParameterDefinition"],
        payable_in_tokens: list[str],
        only_owner: bool,
        title: str = "",
    ) -> None:
        self.name = name
        self.docs = docs
        self.mutability = mutability
        self.inputs = inputs
        self.outputs = outputs
        self.payable_in_tokens = payable_in_tokens
        self.only_owner = only_owner
        self.title = title

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EndpointDefinition":
        inputs = [ParameterDefinition.from_dict(item) for item in data["inputs"]]
        outputs = [ParameterDefinition.from_dict(item) for item in data["outputs"]]

        return cls(
            name=data.get("name", ""),
            docs=data.get("docs", ""),
            mutability=data.get("mutability", ""),
            inputs=inputs,
            outputs=outputs,
            payable_in_tokens=data.get("payableInTokens", []),
            only_owner=data.get("onlyOwner", False),
            title=data.get("title", ""),
        )

    def __repr__(self):
        return f"EndpointDefinition(name={self.name})"


class NullEndpointDefinition(EndpointDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="",
            docs="",
            mutability="",
            inputs=[],
            outputs=[],
            payable_in_tokens=[],
            only_owner=False,
            title="",
        )

    def __repr__(self):
        return "NullEndpointDefinition()"


class ParameterDefinition:
    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParameterDefinition":
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
        )

    def __repr__(self):
        return f"ParameterDefinition(name={self.name}, type={self.type})"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ParameterDefinition) and self.name == value.name and self.type == value.type


class TypesDefinitions:
    def __init__(
        self,
        enums: list["EnumDefinition"],
        explicit_enums: list["ExplicitEnumDefinition"],
        structs: list["StructDefinition"],
    ) -> None:
        self.enums: dict[str, EnumDefinition] = {enum.name: enum for enum in enums}
        self.explicit_enums: dict[str, ExplicitEnumDefinition] = {enum.name: enum for enum in explicit_enums}
        self.structs: dict[str, StructDefinition] = {struct.name: struct for struct in structs}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TypesDefinitions":
        enums: list[EnumDefinition] = []
        explicit_enums: list[ExplicitEnumDefinition] = []
        structs: list[StructDefinition] = []

        for name, definition in data.items():
            kind = definition["type"]

            if kind == "enum":
                enums.append(EnumDefinition.from_dict(name, definition))
            elif kind == "explicit-enum":
                explicit_enums.append(ExplicitEnumDefinition.from_dict(name, definition))
            elif kind == "struct":
                structs.append(StructDefinition.from_dict(name, definition))
            else:
                raise ValueError(f"Unsupported kind of custom type: {kind}")

        return cls(enums=enums, explicit_enums=explicit_enums, structs=structs)


class EnumDefinition:
    def __init__(self, name: str, variants: list["EnumVariantDefinition"]) -> None:
        self.name = name
        self.variants = variants

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "EnumDefinition":
        variants = [EnumVariantDefinition.from_dict(item) for item in data["variants"]]

        return cls(name=name, variants=variants)

    def __repr__(self):
        return f"EnumDefinition(name={self.name})"


class EnumVariantDefinition:
    def __init__(self, name: str, discriminant: int, fields: list["FieldDefinition"]) -> None:
        self.name = name
        self.discriminant = discriminant
        self.fields = fields

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnumVariantDefinition":
        fields = [FieldDefinition.from_dict(item) for item in data.get("fields", [])]

        return cls(
            name=data.get("name", ""),
            discriminant=data.get("discriminant", 0),
            fields=fields,
        )

    def __repr__(self):
        return f"EnumVariantDefinition(name={self.name}, discriminant={self.discriminant})"


class ExplicitEnumDefinition:
    def __init__(self, name: str, variants: list["ExplicitEnumVariantDefinition"]) -> None:
        self.name = name
        self.variants = variants

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "ExplicitEnumDefinition":
        variants = [ExplicitEnumVariantDefinition.from_dict(item) for item in data["variants"]]

        return cls(name=name, variants=variants)

    def __repr__(self):
        return f"ExplicitEnumDefinition(name={self.name})"


class ExplicitEnumVariantDefinition:
    def __init__(self, name: str) -> None:
        self.name = name

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExplicitEnumVariantDefinition":
        return cls(name=data.get("name", ""))

    def __repr__(self):
        return f"ExplicitEnumVariantDefinition(name={self.name})"


class StructDefinition:
    def __init__(self, name: str, fields: list["FieldDefinition"]) -> None:
        self.name = name
        self.fields = fields

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> "StructDefinition":
        fields = [FieldDefinition.from_dict(item) for item in data["fields"]]

        return cls(name=name, fields=fields)

    def __repr__(self):
        return f"StructDefinition(name={self.name})"


class FieldDefinition:
    def __init__(self, name: str, description: str, type: str) -> None:
        self.name = name
        self.description = description
        self.type = type

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldDefinition":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=data.get("type", ""),
        )

    def __repr__(self):
        return f"FieldDefinition(name={self.name}, type={self.type})"


class EventDefinition:
    def __init__(self, identifier: str, inputs: list["EventTopicDefinition"]) -> None:
        self.identifier = identifier
        self.inputs = inputs

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventDefinition":
        inputs = [EventTopicDefinition.from_dict(item) for item in data["inputs"]]

        return cls(identifier=data["identifier"], inputs=inputs)

    def __repr__(self):
        return f"EventDefinition(identifier={self.identifier})"


class EventTopicDefinition:
    def __init__(self, name: str, type: str, indexed: bool) -> None:
        self.name = name
        self.type = type
        self.indexed = indexed

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventTopicDefinition":
        return cls(name=data["name"], type=data["type"], indexed=data.get("indexed", False))

    def __repr__(self):
        return f"EventTopicDefinition(name={self.name})"
