from typing import Any


class ErrBadAddress(Exception):
    def __init__(self, address: Any) -> None:
        super().__init__(f"Bad address: {address}")


class ErrCannotSerializeArgument(Exception):
    def __init__(self, arg: Any) -> None:
        super().__init__(f"Cannot serialize: {arg}")
