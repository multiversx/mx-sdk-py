from typing import Any


class BadPubkeyLengthError(Exception):
    def __init__(self, actual: int, expected: int) -> None:
        super().__init__(f"Bad pubkey length: actual = {actual}, expected = {expected}")


class BadAddressError(Exception):
    def __init__(self, address: Any) -> None:
        super().__init__(f"Bad address: {address}")


class NotEnoughGasError(Exception):
    def __init__(self, gas_limit: int) -> None:
        super().__init__(f"Not enough gas provided: {gas_limit}")


class BadUsageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidTokenIdentifierError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParseTransactionOnNetworkError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
