from typing import Any


class BadPubkeyLengthError(Exception):
    def __init__(self, actual: int, expected: int) -> None:
        super().__init__(f"Bad pubkey length: actual = {actual}, expected = {expected}")


class BadAddressError(Exception):
    def __init__(self, address: Any) -> None:
        super().__init__(f"Bad address: {address}")


class ListsLengthMismatchError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotEnoughGasError(Exception):
    def __init__(self, gas_limit: int) -> None:
        super().__init__(f"Not enough gas provided: {gas_limit}")


class BadUsageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidTokenIdentifierError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidInnerTransactionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParseTransactionOnNetworkError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SmartContractQueryError(Exception):
    def __init__(self, return_code: str, message: str) -> None:
        super().__init__(message)
        self.return_code = return_code


class ArgumentSerializationError(Exception):
    def __init__(self, message: str = "Unable to encode arguments: unsupported format or missing ABI file") -> None:
        super().__init__(message)
