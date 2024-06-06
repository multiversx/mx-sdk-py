from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.shared import convert_native_value_to_list


class MultiValue:
    def __init__(self, items: List[Any]):
        self.items = items

    def set_payload(self, value: Any):
        native_items, _ = convert_native_value_to_list(value)

        if len(value) != len(self.items):
            raise ValueError(f"for multi-value, expected {len(self.items)} items, got {len(value)}")

        for item, native_item in zip(self.items, native_items):
            item.set_payload(native_item)


class VariadicValues:
    def __init__(self,
                 items: Optional[List[Any]] = None,
                 item_creator: Optional[Callable[[], Any]] = None) -> None:
        self.items = items or []
        self.item_creator = item_creator



class OptionalValue:
    def __init__(self, value: Any = None):
        self.value = value

