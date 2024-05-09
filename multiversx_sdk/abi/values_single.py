from typing import Any, Callable, List, Optional, Protocol


class BoolValue:
    def __init__(self, value: bool = False) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BoolValue) and self.value == other.value


class U8Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U8Value) and self.value == other.value


class U16Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U16Value) and self.value == other.value


class U32Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U32Value) and self.value == other.value


class U64Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, U64Value) and self.value == other.value


class I8Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I8Value) and self.value == other.value


class I16Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I16Value) and self.value == other.value


class I32Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I32Value) and self.value == other.value


class I64Value:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, I64Value) and self.value == other.value


class BigUIntValue:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BigUIntValue) and self.value == other.value


class BigIntValue:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BigIntValue) and self.value == other.value


class IAddress(Protocol):
    """
    For internal use only.
    """

    def get_public_key(self) -> bytes:
        ...


class AddressValue:
    def __init__(self, value: bytes) -> None:
        self.value = value

    @classmethod
    def from_address(cls, address: IAddress) -> "AddressValue":
        return cls(address.get_public_key())

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AddressValue) and self.value == other.value


class StringValue:
    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StringValue) and self.value == other.value


class BytesValue:
    def __init__(self, value: bytes) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, BytesValue) and self.value == other.value


class Field:
    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Field) and self.name == other.name and self.value == other.value


class StructValue:
    def __init__(self, fields: List[Field]) -> None:
        self.fields = fields

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StructValue) and self.fields == other.fields


class EnumValue:
    def __init__(self, discriminant: int, fields: List[Field]) -> None:
        self.discriminant = discriminant
        self.fields = fields

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, EnumValue)
            and self.discriminant == other.discriminant
            and self.fields == other.fields
        )


class OptionValue:
    def __init__(self, value: Optional[Any] = None) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OptionValue) and self.value == other.value


class InputListValue:
    def __init__(self, items: List[Any]) -> None:
        self.items = items

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InputListValue) and self.items == other.items


class OutputListValue:
    def __init__(self, item_creator: Callable[[], Any]) -> None:
        self.items: List[Any] = []
        self.item_creator = item_creator

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, OutputListValue)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )
