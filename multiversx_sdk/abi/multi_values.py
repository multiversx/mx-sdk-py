from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.shared import convert_native_value_to_list


class MultiValue:
    def __init__(self, items: List[Any]):
        self.items = items


class VariadicValues:
    def __init__(self,
                 items: Optional[List[Any]] = None,
                 item_creator: Optional[Callable[[], Any]] = None) -> None:
        self.items = items or []
        self.item_creator = item_creator


class OptionalValue:
    def __init__(self, value: Any = None):
        self.value = value

