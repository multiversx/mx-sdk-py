from typing import Any


class ErrBadPubkeyLength(Exception):
    def __init__(self, actual: int, expected: int) -> None:
        super().__init__(f"Bad pubkey length: actual = {actual}, expected = {expected}")


class ErrBadAddress(Exception):
    def __init__(self, address: Any) -> None:
        super().__init__(f"Bad address: {address}")


class ErrCannotSerializeArgument(Exception):
    def __init__(self, arg: Any) -> None:
        super().__init__(f"Cannot serialize: {arg}")


class ErrInvalidRelayerV1BuilderArguments(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid arguments for relayed v1 builder")


class ErrInvalidRelayerV2BuilderArguments(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid arguments for relayed v2 builder")


class ErrInvalidGasLimitForInnerTransaction(Exception):
    def __init__(self) -> None:
        super().__init__("Gas limit should be 0 for the inner transaction for relayed v2")


class ErrListsLengthDoNotMatch(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
