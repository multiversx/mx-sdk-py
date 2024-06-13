from typing import Any

from multiversx_sdk.abi.interface import IPayloadHolder


class OptionalValue(IPayloadHolder):
    def __init__(self, value: Any = None):
        self.value = value

    def set_payload(self, value: Any):
        if value is None:
            self.value = None
            return

        if self.value is None:
            raise ValueError("placeholder value of optional should be set before calling set_payload")

        if isinstance(value, OptionalValue):
            self.value = value.value
            return

        self.value.set_payload(value)

    def get_payload(self) -> Any:
        if self.value is None:
            return None

        return self.value.get_payload()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OptionalValue) and self.value == other.value
