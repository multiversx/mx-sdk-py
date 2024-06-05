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


class ErrListsLengthMismatch(Exception):
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


class ParseTransactionOutcomeError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SmartContractQueryError(Exception):
    def __init__(self, return_code: str, message: str) -> None:
        super().__init__(message)
        self.return_code = return_code
