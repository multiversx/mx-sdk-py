from typing import Any

from multiversx_sdk.abi.interface import SingleValue


class Field:
    def __init__(self, name: str, value: SingleValue) -> None:
        self.name = name
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Field) and self.name == other.name and self.value == other.value
