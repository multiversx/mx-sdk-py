from typing import Any, Optional, Union

from multiversx_sdk.abi.interface import IPayloadHolder, ISingleValue
from multiversx_sdk.abi.multi_value import MultiValue


class OptionalValue(IPayloadHolder):
    def __init__(self, value: Optional[Union[ISingleValue, MultiValue]] = None):
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
