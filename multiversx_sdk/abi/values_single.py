from typing import Protocol


class IAddress(Protocol):
    def get_public_key(self) -> bytes:
        ...


class AddressValue:
    def __init__(self, value: bytes) -> None:
        self.value = value

    @classmethod
    def from_address(cls, address: IAddress) -> "AddressValue":
        return cls(address.get_public_key())


class BoolValue:
    def __init__(self, value: bool) -> None:
        self.value = value
