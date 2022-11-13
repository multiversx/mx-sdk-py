
from typing import Any, List

from erdpy_core.args_serializer import args_to_string
from erdpy_core.constants import ARGUMENTS_SEPARATOR
from erdpy_core.transaction_payload import TransactionPayload


class FunctionCallBuilder:
    """
    A builder for TransactionPayload objects, to be used for Smart Contract calls or built-in function calls.
    """

    def __init__(self) -> None:
        self.function_name = ""
        self.arguments: List[Any] = []

    def set_function(self, function_name: str) -> None:
        self.function_name = function_name

    def add_argument(self, arg: Any) -> None:
        self.arguments.append(arg)

    def set_arguments(self, args: List[Any]) -> None:
        self.arguments = args

    def build(self) -> TransactionPayload:
        data = self.function_name

        if self.arguments:
            data = f"{data}{ARGUMENTS_SEPARATOR}{args_to_string(self.arguments)}"

        return TransactionPayload.from_str(data)
