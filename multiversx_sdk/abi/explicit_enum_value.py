from typing import Any

from multiversx_sdk.abi.string_value import StringValue


class ExplicitEnumValue(StringValue):
    def __init__(self, value: str = "") -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ExplicitEnumValue) and self.value == other.value
