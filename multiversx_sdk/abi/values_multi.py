from typing import Any, Callable, List, Optional


class MultiValue:
    def __init__(self, items: List[Any]):
        self.items = items

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MultiValue) and self.items == other.items

    # def set_native_object(self, value: Any):
    #     if isinstance(value, List):
    #         if len(value) != len(self.items):
    #             raise ValueError("invalid value length")

    # def get_native_object(self) -> Any:
    #     return [item.get_native_object() for item in self.items]


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

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, VariadicValues)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )


class OptionalValue:
    def __init__(self, value: Any = None):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OptionalValue) and self.value == other.value
