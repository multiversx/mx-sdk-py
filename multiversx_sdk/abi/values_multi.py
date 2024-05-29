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
