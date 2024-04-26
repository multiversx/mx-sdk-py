from typing import Protocol


class U8Value:
    def __init__(self, value: int) -> None:
        self.value = value


class U16Value:
    def __init__(self, value: int) -> None:
        self.value = value


class U32Value:
    def __init__(self, value: int) -> None:
        self.value = value


class U64Value:
    def __init__(self, value: int) -> None:
        self.value = value


class I8Value:
    def __init__(self, value: int) -> None:
        self.value = value


class I16Value:
    def __init__(self, value: int) -> None:
        self.value = value


class I32Value:
    def __init__(self, value: int) -> None:
        self.value = value


class I64Value:
    def __init__(self, value: int) -> None:
        self.value = value


class BigUIntValue:
    def __init__(self, value: int) -> None:
        self.value = value


class BigIntValue:
    def __init__(self, value: int) -> None:
        self.value = value


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


class StringValue:
    def __init__(self, value: str) -> None:
        self.value = value


class BoolValue:
    def __init__(self, value: bool) -> None:
        self.value = value
