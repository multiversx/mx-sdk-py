from typing import Any, Callable, Optional, Union

from multiversx_sdk.abi.interface import IPayloadHolder, ISingleValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.shared import convert_native_value_to_list


class CountedVariadicValues(IPayloadHolder):
    def __init__(
        self,
        items: Optional[list[Union[ISingleValue, MultiValue]]] = None,
        item_creator: Optional[Callable[[], Union[ISingleValue, MultiValue]]] = None,
    ) -> None:
        self.items = items or []
        self.length = len(self.items)

        self.item_creator = item_creator

    def set_payload(self, value: Any):
        if not self.item_creator:
            raise ValueError("populating variadic values from a native object requires the item creator to be set")

        native_items, _ = convert_native_value_to_list(value)
        self.length = len(native_items)

        self.items.clear()

        for native_item in native_items:
            item = self.item_creator()
            item.set_payload(native_item)
            self.items.append(item)

    def get_payload(self) -> Any:
        return [item.get_payload() for item in self.items]

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, CountedVariadicValues)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )

    def __iter__(self) -> Any:
        return iter(self.items)
