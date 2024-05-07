from typing import Any, Callable, List


class InputMultiValue:
    def __init__(self, items: List[Any]):
        self.items = items


class OutputMultiValue:
    def __init__(self, items: List[Any]):
        self.items = items


class InputVariadicValues:
    def __init__(self, items: List[Any]):
        self.items = items


class OutputVariadicValues:
    def __init__(self, items: List[Any], item_creator: Callable[[], Any]):
        self.items = items
        self.item_creator = item_creator


class InputOptionalValue:
    def __init__(self, value: Any):
        self.value = value


class OutputOptionalValue:
    def __init__(self, value: Any):
        self.value = value
