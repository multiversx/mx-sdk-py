from typing import Any, Callable, List


class InputMultiValue:
    def __init__(self, items: List[Any]):
        self.items = items

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InputMultiValue) and self.items == other.items


class OutputMultiValue:
    def __init__(self, items: List[Any]):
        self.items = items

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OutputMultiValue) and self.items == other.items


class InputVariadicValues:
    def __init__(self, items: List[Any]):
        self.items = items

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InputVariadicValues) and self.items == other.items


class OutputVariadicValues:
    def __init__(self, item_creator: Callable[[], Any]):
        self.item_creator = item_creator
        self.items: List[Any] = []

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, OutputVariadicValues)
            and self.items == other.items
            and self.item_creator == other.item_creator
        )


class InputOptionalValue:
    def __init__(self, value: Any = None):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InputOptionalValue) and self.value == other.value


class OutputOptionalValue:
    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OutputOptionalValue) and self.value == other.value
