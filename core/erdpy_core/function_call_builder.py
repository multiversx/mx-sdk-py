
from typing import Any, List

from erdpy_core.constants import ARGUMENTS_SEPARATOR
from erdpy_core.serializer import args_to_string
from erdpy_core.transaction_payload import TransactionPayload


class FunctionCallBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract calls or built-in function calls.
    """

    def __init__(self, function_name: str, arguments: List[Any] = []) -> None:
        self.function_name = function_name
        self.arguments: List[Any] = arguments

    def build(self) -> TransactionPayload:
        data = self.function_name

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)
