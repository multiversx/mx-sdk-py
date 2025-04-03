from typing import Any, Union

from multiversx_sdk.abi.interface import IPayloadHolder, ISingleValue
from multiversx_sdk.abi.shared import convert_native_value_to_list


class MultiValue(IPayloadHolder):
    def __init__(self, items: list[Union[ISingleValue, "MultiValue"]]):
        self.items = items

    def set_payload(self, value: Any):
        native_items, _ = convert_native_value_to_list(value)

        if len(value) != len(self.items):
            raise ValueError(f"for multi-value, expected {len(self.items)} items, got {len(value)}")

        for item, native_item in zip(self.items, native_items):
            item.set_payload(native_item)

    def get_payload(self) -> Any:
        return [item.get_payload() for item in self.items]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MultiValue) and self.items == other.items

    def __iter__(self) -> Any:
        return iter(self.items)
