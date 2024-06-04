from typing import Any, Callable, List, Optional

from multiversx_sdk.abi.shared import convert_native_value_to_list


class MultiValue:
    def __init__(self, items: List[Any]):
        self.items = items

    def set_native_object(self, value: Any):
        native_items, _ = convert_native_value_to_list(value)

        if len(value) != len(self.items):
            raise ValueError(f"for multi-value, expected {len(self.items)} items, got {len(value)}")

        for item, native_item in zip(self.items, native_items):
            item.set_native_object(native_item)

    def get_native_object(self) -> Any:
        return [item.get_native_object() for item in self.items]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MultiValue) and self.items == other.items

    def __iter__(self) -> Any:
        return iter(self.items)


class VariadicValues:
    def __init__(self,
                 items: Optional[List[Any]] = None,
                 item_creator: Optional[Callable[[], Any]] = None) -> None:
        self.items = items or []
        self.item_creator = item_creator

    def set_native_object(self, value: Any):
        if not self.item_creator:
            raise ValueError("populating variadic values from a native object requires the item creator to be set")

        native_items, _ = convert_native_value_to_list(value)

        self.items.clear()

        for native_item in native_items:
            item = self.item_creator()
            item.set_native_object(native_item)
            self.items.append(item)

    def get_native_object(self) -> Any:
        return [item.get_native_object() for item in self.items]

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, VariadicValues)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )

    def __iter__(self) -> Any:
        return iter(self.items)


class OptionalValue:
    def __init__(self, value: Any = None):
        self.value = value

    def set_native_object(self, value: Any):
        if value is None:
            self.value = None
            return

        if self.value is None:
            raise ValueError("placeholder value of optional should be set before calling set_native_object")

        self.value.set_native_object(value)

    def get_native_object(self) -> Any:
        if self.value is None:
            return None

        return self.value.get_native_object()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OptionalValue) and self.value == other.value
